"""Build voice.wav (44.1 kHz stereo, on the video timeline) from Piper lines.
Usage: python3 voice.py MODEL SPEAKER LENGTH_SCALE OUT.wav"""
import sys, subprocess, io, wave, numpy as np
from scipy.signal import resample_poly, butter, sosfilt
model, spk, ls, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
SR = 44100; DUR = 31.9
# (window start, window end) for each line, in video seconds
WIN = [(0.08, 1.84), (2.15, 3.75), (9.25, 13.95), (14.35, 21.1), (21.45, 27.05), (27.5, 31.3)]
lines = open("voix-off.txt", encoding="utf-8").read().strip().split("\n")
track = np.zeros(int(SR * DUR))
def synth(text, scale=None):
    raw = subprocess.run([sys.executable, "-m", "piper", "-m", model, "-s", spk, "--length-scale", str(scale or ls),
                          "--noise-scale", "0.6", "--noise-w-scale", "0.7", "--sentence-silence", "0.18", "--output-raw"],
                         input=text.encode(), capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(float) / 32768
    return resample_poly(x, 2, 1)          # Piper outputs 22.05 kHz
def trim(x, thr=.01):
    a = np.where(np.abs(x) > thr)[0]
    return x[max(0, a[0] - 400): a[-1] + 2000] if len(a) else x
report = []
for (w0, w1), text in zip(WIN, lines):
    x = trim(synth(text))
    d = len(x) / SR
    # if a line runs long, re-synthesise it slightly faster (pitch unchanged), at most 15 % faster
    if d > w1 - w0:
        x = trim(synth(text, float(ls) * max(.85, (w1 - w0) / d * .98)))
        d = len(x) / SR
    i = int(w0 * SR); track[i:i + len(x)] += x[: len(track) - i]
    report.append((round(w0, 2), round(d, 2), round(w1 - w0, 2), "OK" if d <= w1 - w0 + .05 else "LONG"))
# voice processing: high-pass, presence lift, gentle compression, level
sos = butter(2, 90, "high", fs=SR, output="sos"); track = sosfilt(sos, track)
pres = sosfilt(butter(2, [2500, 5000], "band", fs=SR, output="sos"), track); track = track + .25 * pres
env = sosfilt(butter(1, 12, "low", fs=SR, output="sos"), np.abs(track))
thr = .08; gr = np.where(env > thr, (thr * (env / thr) ** (1 / 2.5)) / np.maximum(env, 1e-9), 1)
track = track * gr
track = track / np.max(np.abs(track)) * .7
st = np.stack([track, track], 1)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
for r in report: print(r)
