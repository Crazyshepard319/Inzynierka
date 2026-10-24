

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import logging
import warnings

# flirpy generuje dziwne ostrzeżenia/logi dla części plików SEQ (bug w bibliotece).
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API.*")
logging.getLogger().setLevel(logging.ERROR)
from flirpy.io.seq import Seq

INZ = Path(__file__).resolve().parent.parent      # folder Inzynierka
# nagranie do rozpakowania: nowe w dane/dane_termowizja/, stare w archiwum/dane/nagrania_termowizja/
filepath = str(INZ / "archiwum" / "dane" / "nagrania_termowizja" / "Rec-000040.seq")
NUM_FRAMES_TO_SAVE = 10
SAVE_ALL_FRAMES = False  #jeśli True, to zapisze wszystkie klatki, jeśli False, to tylko NUM_FRAMES_TO_SAVE klatek
HORIZONTAL_ROLL_PIXELS = 66  # to offset potrzebny na zignorowanie nagłówka pliku SEQ dla FLIR A655sc

seq = Seq(filepath)
frame0 = seq[0]
shape = None
if hasattr(frame0, 'get_image'):
	arr = frame0.get_image()
	shape = arr.shape
elif hasattr(frame0, 'shape'):
	shape = frame0.shape
else:
	arr = np.array(frame0)
	shape = arr.shape

print(f"Ustawiony rozmiar klatki: {shape}")

# --- Zbierz klatki do tablicy ---
num_to_save = len(seq) if SAVE_ALL_FRAMES else min(NUM_FRAMES_TO_SAVE, len(seq))
frames = []
for i in range(num_to_save):
	frm = seq[i]
	if hasattr(frm, 'get_image'):
		frm = frm.get_image()
	else:
		frm = np.array(frm)
	if HORIZONTAL_ROLL_PIXELS:
		# Korekta zawijania obrazu (przesunięcie kolumn w poziomie).
		frm = np.roll(frm, HORIZONTAL_ROLL_PIXELS, axis=1)
	frames.append(frm)
frames = np.stack(frames)

# --- Normalizacja i zapis PNG ---
def normalize(img):
	p1, p99 = np.percentile(img, [1, 99])
	img = np.clip((img - p1) / (p99 - p1), 0, 1)
	return img

# outdir = Path("out_seq")
# outdir.mkdir(exist_ok=True)
#
# for i, img in enumerate(frames):
# 	img_norm = normalize(img)
# 	plt.imsave(outdir / f"frame_{i:03d}.png", img_norm, cmap="inferno")
# 	print(f"Zapisano: {outdir / f'frame_{i:03d}.png'}")


# --- Zapisz klatek jako PNG z normalizacją ---
_seq = Path(filepath)
# klatki obok nagrania, gdy jest w dane/ (np. dane_termowizja/znamie_01/Rec-0000NN/),
# inaczej (np. nagranie z archiwum) do dane/dane_termowizja/<nagranie>/
out_dir = _seq.with_suffix("") if (INZ / "dane") in _seq.parents else INZ / "dane" / "dane_termowizja" / _seq.stem
out_dir.mkdir(parents=True, exist_ok=True)
num_to_save = frames.shape[0] if SAVE_ALL_FRAMES else min(NUM_FRAMES_TO_SAVE, frames.shape[0])
percentile_range = (2, 98)
lo, hi = percentile_range
vmin = float(np.nanpercentile(frames, lo))
vmax = float(np.nanpercentile(frames, hi))
print(f"Normalizacja: vmin={vmin:.3f}, vmax={vmax:.3f} (percentile={percentile_range})")
for i in range(num_to_save):
	frm = np.array(frames[i], dtype='float64')
	if not np.isfinite(frm).all():
		frm = np.nan_to_num(frm, nan=np.nanmedian(frm))
	# Normalizacja
	if np.isclose(vmax, vmin):
		norm = np.full(frm.shape, 0.5, dtype='float32')
	else:
		eps = 1e-12
		norm = (frm - vmin) / (vmax - vmin + eps)
	out_path = out_dir / f"frame_{i:03d}.png"
	plt.imsave(str(out_path), norm, cmap='inferno', vmin=0.0, vmax=1.0)
	print(f"Zapisano: {out_path}  (used_vmin={vmin:.3f}, used_vmax={vmax:.3f})")

if hasattr(seq, 'close'):
	try:
		seq.close()
	except Exception:
		pass
