"""
U-Net (Ronneberger i in., MICCAI 2015) w wersji zmniejszonej do segmentacji znacznika Π na termowizji.

Koder: 4 poziomy (dwa sploty 3x3 + BatchNorm + ReLU, potem max-pooling 2x2), dekoder: splot
transponowany 2x2 (krok 2), sklejenie z mapa cech kodera (polaczenie skrotowe) i dwa sploty 3x3.
Kanaly 16-32-64-128, dno 256 (ok. 1,9 mln parametrow); wyjscie: 1 kanal (logit). Wejscie 240 x 320
dzieli sie przez 16, wiec poziomy kodera i dekodera maja zgodne rozmiary bez przycinania.
Tylko operacje obslugiwane przez cv2.dnn (Conv, BatchNorm, Relu, MaxPool, ConvTranspose, Concat,
Sigmoid), wiec model wyeksportowany do ONNX dziala w aplikacji bez PyTorch.
"""
import torch
import torch.nn as nn


class Blok(nn.Sequential):
    """Dwa sploty 3x3 z BatchNorm i ReLU."""

    def __init__(self, wej, wyj):
        super().__init__(
            nn.Conv2d(wej, wyj, 3, padding=1, bias=False), nn.BatchNorm2d(wyj), nn.ReLU(inplace=True),
            nn.Conv2d(wyj, wyj, 3, padding=1, bias=False), nn.BatchNorm2d(wyj), nn.ReLU(inplace=True))


class UNet(nn.Module):
    def __init__(self, kanaly=(16, 32, 64, 128, 256), wejscie=1):
        super().__init__()
        self.kanaly = tuple(kanaly)
        self.koder = nn.ModuleList()
        c = wejscie
        for k in kanaly[:-1]:
            self.koder.append(Blok(c, k))
            c = k
        self.pool = nn.MaxPool2d(2)
        self.dno = Blok(kanaly[-2], kanaly[-1])
        self.gora = nn.ModuleList()
        self.dekoder = nn.ModuleList()
        for k_wyz, k in zip(kanaly[:0:-1], kanaly[-2::-1]):
            self.gora.append(nn.ConvTranspose2d(k_wyz, k, 2, stride=2))
            self.dekoder.append(Blok(2 * k, k))
        self.wyjscie = nn.Conv2d(kanaly[0], 1, 1)

    def forward(self, x):
        skroty = []
        for blok in self.koder:
            x = blok(x)
            skroty.append(x)
            x = self.pool(x)
        x = self.dno(x)
        for gora, blok, s in zip(self.gora, self.dekoder, reversed(skroty)):
            x = blok(torch.cat([gora(x), s], dim=1))
        return self.wyjscie(x)                      # logity (B, 1, H, W)


class ZSigmoida(nn.Module):
    """Model do eksportu: prawdopodobienstwo zamiast logitu."""

    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        return torch.sigmoid(self.model(x))


def liczba_parametrow(model):
    return sum(p.numel() for p in model.parameters())
