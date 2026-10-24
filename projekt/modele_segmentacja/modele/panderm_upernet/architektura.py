"""
PanDerm (ViT-L/16, CAE) + UperNet - architektura z repozytorium autorow
(repozytoria/PanDerm/segmentation/models: cae_backbone.py, cae_config.py, cae_seg.py)
przeniesiona do czystego PyTorch, bez mmcv/mmsegmentation.

Dlaczego: srodowisko autorow (mmcv 2.1 + mmseg 1.2.2) nie instaluje sie
(PanDerm issue #11: "No module named 'mmcv._ext'"), a z OpenMMLab model uzywa
tylko glowicy UPerHead i ConvModule. Odtworzono je 1:1 - nazwy modulow sa te same,
wiec checkpoint autorow (klucze "model.segmentor.*") wczytuje sie bez zmian.
Jedyna podmiana: SyncBatchNorm -> BatchNorm2d (na jednym GPU dzialaja identycznie).
"""
import math
from functools import partial

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.checkpoint as checkpoint


# ── zamienniki funkcji z timm ────────────────────────────────────────────────

def to_2tuple(x):
    return tuple(x) if isinstance(x, (tuple, list)) else (x, x)


def drop_path(x, drop_prob=0., training=False):
    if drop_prob == 0. or not training:
        return x
    keep = 1 - drop_prob
    shape = (x.shape[0],) + (1,) * (x.ndim - 1)
    maska = x.new_empty(shape).bernoulli_(keep)
    return x * maska / keep


def trunc_normal_(t, std=1.):
    return nn.init.trunc_normal_(t, mean=0., std=std, a=-2., b=2.)


# ── backbone CAE (cae_backbone.py autorow) ───────────────────────────────────

class DropPath(nn.Module):
    def __init__(self, drop_prob=None):
        super().__init__()
        self.drop_prob = drop_prob

    def forward(self, x):
        return drop_path(x, self.drop_prob, self.training)


class Mlp(nn.Module):
    def __init__(self, in_features, hidden_features=None, out_features=None, act_layer=nn.GELU, drop=0.):
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        self.fc1 = nn.Linear(in_features, hidden_features)
        self.act = act_layer()
        self.fc2 = nn.Linear(hidden_features, out_features)
        self.drop = nn.Dropout(drop)

    def forward(self, x):
        return self.drop(self.fc2(self.act(self.fc1(x))))


class Attention(nn.Module):
    def __init__(self, dim, num_heads=8, qkv_bias=False, qk_scale=None, attn_drop=0., proj_drop=0.):
        super().__init__()
        self.num_heads = num_heads
        head_dim = dim // num_heads
        all_head_dim = head_dim * num_heads
        self.scale = qk_scale or head_dim ** -0.5
        self.qkv = nn.Linear(dim, all_head_dim * 3, bias=False)
        if qkv_bias:
            self.q_bias = nn.Parameter(torch.zeros(all_head_dim))
            self.v_bias = nn.Parameter(torch.zeros(all_head_dim))
        else:
            self.q_bias = self.v_bias = None
        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(all_head_dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

    def forward(self, x):
        B, N, C = x.shape
        qkv_bias = None
        if self.q_bias is not None:
            qkv_bias = torch.cat((self.q_bias, torch.zeros_like(self.v_bias, requires_grad=False), self.v_bias))
        qkv = F.linear(input=x, weight=self.qkv.weight, bias=qkv_bias)
        q, k, v = qkv.reshape(B, N, 3, self.num_heads, -1).permute(2, 0, 3, 1, 4)
        attn = ((q * self.scale) @ k.transpose(-2, -1)).softmax(dim=-1)
        attn = self.attn_drop(attn)
        x = (attn @ v).transpose(1, 2).reshape(B, N, -1)
        return self.proj_drop(self.proj(x))


class Block(nn.Module):
    def __init__(self, dim, num_heads, mlp_ratio=4., qkv_bias=False, qk_scale=None, drop=0., attn_drop=0.,
                 drop_path=0., init_values=None, act_layer=nn.GELU, norm_layer=nn.LayerNorm):
        super().__init__()
        self.norm1 = norm_layer(dim)
        self.attn = Attention(dim, num_heads=num_heads, qkv_bias=qkv_bias, qk_scale=qk_scale,
                              attn_drop=attn_drop, proj_drop=drop)
        self.drop_path = DropPath(drop_path) if drop_path > 0. else nn.Identity()
        self.norm2 = norm_layer(dim)
        self.mlp = Mlp(in_features=dim, hidden_features=int(dim * mlp_ratio), act_layer=act_layer, drop=drop)
        if init_values is not None:
            self.gamma_1 = nn.Parameter(init_values * torch.ones(dim))
            self.gamma_2 = nn.Parameter(init_values * torch.ones(dim))
        else:
            self.gamma_1 = self.gamma_2 = None

    def forward(self, x):
        if self.gamma_1 is None:
            x = x + self.drop_path(self.attn(self.norm1(x)))
            return x + self.drop_path(self.mlp(self.norm2(x)))
        x = x + self.drop_path(self.gamma_1 * self.attn(self.norm1(x)))
        return x + self.drop_path(self.gamma_2 * self.mlp(self.norm2(x)))


class PatchEmbed(nn.Module):
    def __init__(self, img_size=224, patch_size=16, in_chans=3, embed_dim=768):
        super().__init__()
        img_size, patch_size = to_2tuple(img_size), to_2tuple(patch_size)
        self.patch_shape = (img_size[0] // patch_size[0], img_size[1] // patch_size[1])
        self.num_patches = self.patch_shape[0] * self.patch_shape[1]
        self.proj = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)

    def forward(self, x):
        x = self.proj(x)
        Hp, Wp = x.shape[2], x.shape[3]
        return x.flatten(2).transpose(1, 2), (Hp, Wp)


class CAE(nn.Module):
    """ViT z wyjsciami z 4 warstw przeskalowanymi do 1/4, 1/8, 1/16, 1/32 (jak w BEiT/CAE dla segmentacji)."""

    def __init__(self, img_size=224, patch_size=16, in_chans=3, embed_dim=1024, depth=24, num_heads=16,
                 mlp_ratio=4., qkv_bias=True, qk_scale=None, drop_rate=0., attn_drop_rate=0.,
                 drop_path_rate=0.15, init_values=1e-5, use_checkpoint=False,
                 out_indices=(7, 11, 15, 23), out_with_norm=True):
        super().__init__()
        norm_layer = partial(nn.LayerNorm, eps=1e-6)
        self.embed_dim = embed_dim
        self.patch_embed = PatchEmbed(img_size, patch_size, in_chans, embed_dim)
        self.out_indices = list(out_indices)
        self.use_checkpoint = use_checkpoint

        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        # use_abs_pos_emb=False, use_sincos_pos_embed=True (cae_config.py) -> staly embedding 2D sin-cos
        self.pos_embed = self._sincos_2d(embed_dim)
        self.pos_drop = nn.Dropout(p=drop_rate)

        dpr = [x.item() for x in torch.linspace(0, drop_path_rate, depth)]
        self.blocks = nn.ModuleList([
            Block(dim=embed_dim, num_heads=num_heads, mlp_ratio=mlp_ratio, qkv_bias=qkv_bias, qk_scale=qk_scale,
                  drop=drop_rate, attn_drop=attn_drop_rate, drop_path=dpr[i], norm_layer=norm_layer,
                  init_values=init_values)
            for i in range(depth)])
        trunc_normal_(self.cls_token, std=.02)

        assert patch_size == 16
        self.fpn1 = nn.Sequential(
            nn.ConvTranspose2d(embed_dim, embed_dim, kernel_size=2, stride=2),
            nn.BatchNorm2d(embed_dim),          # SyncBatchNorm u autorow
            nn.GELU(),
            nn.ConvTranspose2d(embed_dim, embed_dim, kernel_size=2, stride=2),
        )
        self.fpn2 = nn.Sequential(nn.ConvTranspose2d(embed_dim, embed_dim, kernel_size=2, stride=2))
        self.fpn3 = nn.Identity()
        self.fpn4 = nn.MaxPool2d(kernel_size=2, stride=2)
        self.norm = norm_layer(embed_dim) if out_with_norm else nn.Identity()
        self.apply(self._init_weights)

    def _sincos_2d(self, embed_dim, temperature=10000.):
        h, w = self.patch_embed.patch_shape
        grid_w, grid_h = torch.meshgrid(torch.arange(w, dtype=torch.float32),
                                        torch.arange(h, dtype=torch.float32), indexing='ij')
        pos_dim = embed_dim // 4
        omega = 1. / (temperature ** (torch.arange(pos_dim, dtype=torch.float32) / pos_dim))
        out_w = torch.einsum('m,d->md', grid_w.flatten(), omega)
        out_h = torch.einsum('m,d->md', grid_h.flatten(), omega)
        pos = torch.cat([torch.sin(out_w), torch.cos(out_w), torch.sin(out_h), torch.cos(out_h)], dim=1)[None]
        pe = nn.Parameter(torch.cat([torch.zeros(1, 1, embed_dim), pos], dim=1))
        pe.requires_grad = False
        return pe

    @staticmethod
    def _init_weights(m):
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def forward(self, x):
        B = x.shape[0]
        x, (Hp, Wp) = self.patch_embed(x)
        x = torch.cat((self.cls_token.expand(B, -1, -1), x), dim=1)
        x = self.pos_drop(x + self.pos_embed)
        cechy = []
        for i, blk in enumerate(self.blocks):
            if self.use_checkpoint and self.training:
                x = checkpoint.checkpoint(blk, x, use_reentrant=False)
            else:
                x = blk(x)
            if i in self.out_indices:
                cechy.append(self.norm(x[:, 1:, :]).permute(0, 2, 1).reshape(B, -1, Hp, Wp).contiguous())
        ops = [self.fpn1, self.fpn2, self.fpn3, self.fpn4]
        return tuple(op(f) for op, f in zip(ops, cechy))


# ── glowica UPerNet (mmseg UPerHead + PPM + mmcv ConvModule) ─────────────────

class ConvModule(nn.Module):
    """conv (bez biasu) -> BatchNorm -> ReLU; nazwy jak w mmcv: conv, bn, activate."""

    def __init__(self, cin, cout, k, padding=0):
        super().__init__()
        self.conv = nn.Conv2d(cin, cout, k, padding=padding, bias=False)
        self.bn = nn.BatchNorm2d(cout)               # SyncBN w cae_config.py
        self.activate = nn.ReLU(inplace=True)
        nn.init.kaiming_normal_(self.conv.weight, mode='fan_out', nonlinearity='relu')
        nn.init.constant_(self.bn.weight, 1)
        nn.init.constant_(self.bn.bias, 0)

    def forward(self, x):
        return self.activate(self.bn(self.conv(x)))


def _resize(x, size):
    return F.interpolate(x, size=size, mode='bilinear', align_corners=False)


class PPM(nn.ModuleList):
    def __init__(self, pool_scales, cin, ch):
        super().__init__([nn.Sequential(nn.AdaptiveAvgPool2d(s), ConvModule(cin, ch, 1)) for s in pool_scales])

    def forward(self, x):
        return [_resize(ppm(x), x.shape[2:]) for ppm in self]


class UPerHead(nn.Module):
    def __init__(self, in_channels=(1024,) * 4, channels=1024, pool_scales=(1, 2, 3, 6), num_classes=2):
        super().__init__()
        self.psp_modules = PPM(pool_scales, in_channels[-1], channels)
        self.bottleneck = ConvModule(in_channels[-1] + len(pool_scales) * channels, channels, 3, padding=1)
        self.lateral_convs = nn.ModuleList([ConvModule(c, channels, 1) for c in in_channels[:-1]])
        self.fpn_convs = nn.ModuleList([ConvModule(channels, channels, 3, padding=1) for _ in in_channels[:-1]])
        self.fpn_bottleneck = ConvModule(len(in_channels) * channels, channels, 3, padding=1)
        self.conv_seg = nn.Conv2d(channels, num_classes, kernel_size=1)
        nn.init.normal_(self.conv_seg.weight, 0, 0.01)
        nn.init.constant_(self.conv_seg.bias, 0)

    def forward(self, inputs):
        x = inputs[-1]
        laterals = [conv(inputs[i]) for i, conv in enumerate(self.lateral_convs)]
        laterals.append(self.bottleneck(torch.cat([x] + self.psp_modules(x), dim=1)))
        for i in range(len(laterals) - 1, 0, -1):
            laterals[i - 1] = laterals[i - 1] + _resize(laterals[i], laterals[i - 1].shape[2:])
        outs = [self.fpn_convs[i](laterals[i]) for i in range(len(laterals) - 1)] + [laterals[-1]]
        for i in range(len(outs) - 1, 0, -1):
            outs[i] = _resize(outs[i], outs[0].shape[2:])
        return self.conv_seg(self.fpn_bottleneck(torch.cat(outs, dim=1)))


class _Segmentor(nn.Module):
    def __init__(self, use_checkpoint=False):
        super().__init__()
        self.backbone = CAE(use_checkpoint=use_checkpoint)
        self.decode_head = UPerHead()


class PanDermUperNet(nn.Module):
    """Odpowiednik CAEv2_seg autorow. Wejscie: (B,3,224,224) znormalizowane (x-0.5)/0.5.
    Wyjscie: logity (B,2,224,224) - klasa 1 = znamie."""

    def __init__(self, use_checkpoint=False):
        super().__init__()
        self.segmentor = _Segmentor(use_checkpoint)

    def forward(self, x):
        out = self.segmentor.decode_head(self.segmentor.backbone(x))
        return _resize(out, x.shape[2:])


# ── wczytywanie wag ──────────────────────────────────────────────────────────

def _stan(plik):
    sd = torch.load(plik, map_location="cpu", weights_only=False)
    for klucz in ("state_dict", "model", "module"):
        if isinstance(sd, dict) and klucz in sd and isinstance(sd[klucz], dict):
            sd = sd[klucz]
    return sd


def wczytaj_backbone_panderm(model, plik):
    """Wagi pretrenowanego PanDerm (panderm_ll_data6_checkpoint-499.pth) do backbone,
    jak w CAEv2_seg.__init__: klucze 'encoder.*' -> backbone. Zwraca (wczytane, pominiete)."""
    sd = _stan(plik)
    nowe = {k.replace('encoder.', ''): v for k, v in sd.items() if 'encoder' in k}
    cel = model.segmentor.backbone.state_dict()
    pasujace = {k: v for k, v in nowe.items() if k in cel and cel[k].shape == v.shape}
    pominiete = [k for k in nowe if k not in pasujace]
    model.segmentor.backbone.load_state_dict(pasujace, strict=False)
    return pasujace, pominiete


def wczytaj_wytrenowany(model, plik):
    """Pelny model po douczeniu: nasz checkpoint albo checkpoint autorow (Lightning)."""
    sd = _stan(plik)
    sd = {(k[6:] if k.startswith("model.") else k): v for k, v in sd.items()}
    braki = model.load_state_dict(sd, strict=False)
    istotne = [k for k in braki.missing_keys if not k.endswith("num_batches_tracked")]
    if istotne:
        raise RuntimeError(f"Checkpoint nie pasuje do modelu, brakuje {len(istotne)} wag, np. {istotne[:3]}")
    return model
