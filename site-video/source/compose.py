"""Original royalty-free track for the Mangue de Côte d'Ivoire TikTok video.
Balafon-style melody, bass, light Afro groove. 100 BPM, C major / A minor pentatonic.
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
TOTAL = 200.7
N = int(TOTAL * SR)
rng = np.random.default_rng(225)

dry = np.zeros((N, 2))      # drums, bass (little reverb)
wet = np.zeros((N, 2))      # melodic bus (sent to reverb)

def mf(m):
    return 440.0 * 2 ** ((m - 69) / 12)

def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)

def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)

def add(bus, t, sig, pan=0.0, gain=1.0):
    t = t + rng.normal(0, 0.004)  # human timing
    i = int(max(t, 0) * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    bus[i:i + len(sig), 0] += sig * l
    bus[i:i + len(sig), 1] += sig * r

def env(n, a, d):
    t = np.arange(n) / SR
    e = np.exp(-t / d)
    na = max(int(a * SR), 1)
    e[:na] *= np.linspace(0, 1, na)
    return e

# ---------------- instruments ----------------
def balafon(m, vel=1.0, length=0.9):
    f = mf(m); n = int(length * SR); t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) * env(n, 0.002, 0.30)
         + 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * env(n, 0.001, 0.06)
         + 0.12 * np.sin(2 * np.pi * f * 9.2 * t) * env(n, 0.001, 0.02))
    # gourd buzz: a little noise riding the tone
    buzz = bp(rng.standard_normal(n), min(f * 2, 8000), min(f * 4, 15000)) * env(n, 0.001, 0.12) * 0.08
    click = hp(rng.standard_normal(n), 2500) * env(n, 0.0005, 0.004) * 0.25
    return (s + buzz + click) * vel * 0.32

def bass(m, vel=1.0, length=0.9):
    f = mf(m); n = int(length * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) + 0.08 * np.sin(2 * np.pi * 3 * f * t)
    e = env(n, 0.006, 0.45); e[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return lp(s * e, 900) * vel * 0.26

def kick(vel=1.0):
    n = int(0.4 * SR); t = np.arange(n) / SR
    f = 45 + 85 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, 0.001, 0.13) * vel * 0.48

def shaker(vel=1.0):
    n = int(0.09 * SR)
    return hp(rng.standard_normal(n), 6000, 4) * env(n, 0.006, 0.025) * vel * 0.11

def clap(vel=1.0):
    n = int(0.25 * SR); x = bp(rng.standard_normal(n), 900, 3200)
    e = np.zeros(n)
    for k, o in enumerate([0, 0.011, 0.022]):
        i = int(o * SR); e[i:] += env(n - i, 0.0005, 0.012 if k < 2 else 0.07)
    return x * e * vel * 0.22

def djembe(kind='tone', vel=1.0):
    n = int(0.3 * SR); t = np.arange(n) / SR
    if kind == 'bass':
        s = np.sin(2 * np.pi * 85 * t) * env(n, 0.002, 0.12)
    elif kind == 'slap':
        s = 0.5 * np.sin(2 * np.pi * 420 * t) * env(n, 0.001, 0.03) + bp(rng.standard_normal(n), 1500, 6000) * env(n, 0.001, 0.025)
    else:
        s = np.sin(2 * np.pi * 300 * t) * env(n, 0.001, 0.07) + 0.2 * bp(rng.standard_normal(n), 600, 2500) * env(n, 0.001, 0.02)
    return s * vel * 0.28

def pad(ms, length):
    n = int(length * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in ms:
        for det in (-0.12, 0.0, 0.12):
            f = mf(m) * 2 ** (det / 12)
            s += 2 * ((f * t + rng.random()) % 1.0) - 1  # saw
    s = lp(s / (len(ms) * 3), 1100, 2)
    a = int(min(0.6, length / 3) * SR); r = int(min(0.8, length / 3) * SR)
    e = np.ones(n); e[:a] = np.linspace(0, 1, a); e[-r:] = np.linspace(1, 0, r)
    return s * e * 0.10

# ---------------- harmony ----------------
# Am - F - C - G   (vi - IV - I - V)
CHORDS = [
    dict(root=45, tones=[69, 72, 76, 81]),   # Am
    dict(root=41, tones=[65, 69, 72, 77]),   # F
    dict(root=48, tones=[67, 72, 76, 79]),   # C
    dict(root=43, tones=[67, 71, 74, 79]),   # G
]
PADS = [[57, 60, 64], [53, 57, 60], [55, 60, 64], [55, 59, 62]]

# melody phrases: (beat, length, midi) over 4 bars
PHRASE_A = [(0, 1, 76), (1, .5, 79), (1.5, 1.5, 81), (3, .5, 79), (3.5, .5, 76),
            (4, 1, 72), (5, .5, 74), (5.5, 1, 76), (6.5, .5, 72), (7, 1, 69),
            (8, .5, 67), (8.5, .5, 72), (9, 1, 76), (10, 1, 79), (11, .5, 76), (11.5, .5, 74),
            (12, 1.5, 74), (13.5, .5, 76), (14, .5, 74), (14.5, .5, 72), (15, 1, 69)]
PHRASE_B = [(0, .5, 81), (.5, 1, 84), (1.5, .5, 81), (2, 1, 79), (3, 1, 76),
            (4, 1.5, 81), (5.5, .5, 79), (6, 1, 76), (7, 1, 72),
            (8, .5, 76), (8.5, .5, 79), (9, 1.5, 84), (10.5, .5, 81), (11, 1, 79),
            (12, 1, 79), (13, .5, 76), (13.5, .5, 74), (14, 2, 76)]

def play_phrase(t0, phrase, vel=0.9, octave=0, pan=0.25):
    for b, L, m in phrase:
        t = t0 + b * BEAT
        if L >= 1:  # balafon roll on long notes
            steps = int(L * 4)
            for k in range(steps):
                add(wet, t + k * BEAT / 4, balafon(m + octave, vel * (0.95 - 0.5 * k / steps)), pan)
        else:
            add(wet, t, balafon(m + octave, vel), pan)

# ---------------- arrangement ----------------
# section flags per bar
def section(bar):
    if bar < 4:   return dict(ost=0.55, shk=0, bas=0, drm=0, mel=None, pad=1)
    if bar < 12:  return dict(ost=0.75, shk=1, bas=1, drm=0, mel=None, pad=1)
    if bar < 28:  return dict(ost=0.6, shk=1, bas=1, drm=1, mel=('A' if bar < 20 else 'B'), pad=1)
    if bar < 36:  return dict(ost=0.8, shk=1, bas=1, drm=1, mel=None, pad=1, busy=1)
    if bar < 52:  return dict(ost=0.6, shk=1, bas=1, drm=1, mel=('A' if bar < 44 else 'B'), pad=1, djm=1)
    if bar < 60:  return dict(ost=0.65, shk=0.6, bas=0, drm=0, mel=None, pad=1)
    if bar < 76:  return dict(ost=0.6, shk=1, bas=1, drm=1, mel=('B' if bar < 68 else 'A'), pad=1, djm=1, octv=1)
    return dict(ost=0.7, shk=0.7, bas=1, drm=0.6, mel=None, pad=1)

OST = [0, 2, 1, 2, 3, 2, 1, 2]   # 8th-note balafon ostinato (index into chord tones)
OST_BUSY = [0, 2, 1, 2, 3, 2, 1, 2, 0, 1, 2, 3, 2, 1, 0, 2]

N_BARS = 82
for bar in range(N_BARS):
    t0 = bar * BAR
    ch = CHORDS[bar % 4]
    s = section(bar)
    if s['pad'] and bar % 1 == 0:
        add(wet, t0, pad(PADS[bar % 4], BAR + 0.4), 0, 1.0)
    # ostinato
    if s.get('busy'):
        for k, idx in enumerate(OST_BUSY):
            add(wet, t0 + k * BEAT / 4, balafon(ch['tones'][idx] - 12, s['ost'] * (1 if k % 4 == 0 else 0.7), 0.6), -0.35)
    else:
        for k, idx in enumerate(OST):
            add(wet, t0 + k * BEAT / 2, balafon(ch['tones'][idx] - 12, s['ost'] * (1 if k % 2 == 0 else 0.75), 0.7), -0.35)
    # bass: root on 1, fifth on "and of 2", root on 3, octave pickup
    if s['bas']:
        r = ch['root']
        for b, m, L, v in [(0, r, 1.2, 1), (1.5, r + 7, 0.5, .8), (2, r, 0.9, .9), (3.5, r + 12, 0.4, .7)]:
            add(dry, t0 + b * BEAT, bass(m, v, L), 0)
    # shaker 16ths with accent
    if s['shk']:
        for k in range(16):
            v = (1.0 if k % 4 == 2 else 0.55 if k % 2 == 0 else 0.4) * s['shk']
            add(dry, t0 + k * BEAT / 4, shaker(v), 0.4 if k % 2 else -0.2)
    # kick + clap
    if s['drm']:
        for b in (0, 1.5, 2.5):
            add(dry, t0 + b * BEAT, kick(s['drm'] * (1 if b == 0 else 0.75)), 0)
        for b in (1, 3):
            add(wet, t0 + b * BEAT, clap(s['drm']), 0.1)
    if s.get('djm'):
        for b, k, v in [(0.75, 'slap', .6), (1.5, 'tone', .8), (2.25, 'tone', .6), (3, 'bass', .9), (3.5, 'slap', .7), (3.75, 'slap', .5)]:
            add(dry, t0 + b * BEAT, djembe(k, v), -0.5)
    # melody (phrases start every 4 bars)
    if s['mel'] and bar % 4 == 0:
        ph = PHRASE_A if s['mel'] == 'A' else PHRASE_B
        play_phrase(t0, ph, 1.35, 0, 0.25)
        if s.get('octv'):
            play_phrase(t0, ph, 0.5, 12, 0.45)

# final chord: Am, rolled, rings out
tf = N_BARS * BAR
for k, m in enumerate([57, 64, 69, 72, 76, 81]):
    add(wet, tf + k * 0.035, balafon(m, 0.8, 3.5), -0.3 + k * 0.12)
add(dry, tf, bass(45, 1.0, 3.0), 0)
add(wet, tf, pad([57, 60, 64, 69], 3.8), 0, 1.2)

# ---------------- mix ----------------
ir_len = int(2.0 * SR)
tt = np.arange(ir_len) / SR
ir = np.stack([rng.standard_normal(ir_len) * np.exp(-tt / 0.45) for _ in range(2)], 1)
ir = np.stack([lp(ir[:, c], 6000) for c in range(2)], 1); ir /= np.abs(ir).sum(0) ** 0.5 * 4
rev = np.stack([fftconvolve(wet[:, c], ir[:, c])[:N] for c in range(2)], 1)
mix = dry + wet + 0.6 * rev
mix = np.stack([hp(mix[:, c], 30) for c in range(2)], 1)

# fades: soft start, fade out over the last 1.6 s
fi = int(0.8 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(1.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5

mix = np.tanh(mix * 1.1) / np.tanh(1.1)          # gentle saturation / limiting
mix /= np.max(np.abs(mix)) * 1.12
wavfile.write('music.wav', SR, (mix * 32767).astype(np.int16))
print('ok', mix.shape[0] / SR)
