"""Original soundtrack for the mango teaser (31.9 s).

A West African-inspired groove synthesised from scratch: balafon (wooden xylophone of the
Senufo in northern Côte d'Ivoire, where the mangoes grow), djembe, shaker and a soft bass,
plus sound effects synced to the picture (stamp, logo, counter, flies, product pops, end chime).
No samples, no copyrighted material.
"""
import numpy as np, sys
GAIN = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
DUR = 31.9
N = int(SR * DUR)
rng = np.random.default_rng(7)

# ---------- timing: map the stage's design time to video time ----------
HOLDS_A = [(2.2, 1.2)]
HOLDS_B = [(2.6, 1.6), (5.0, 0.8), (6.2, 2.0), (10.5, 2.0), (14.0, 1.5)]
def real(d, holds):
    return d + sum(dur for at, dur in holds if at < d)
A = lambda d: real(d, HOLDS_A)           # segment A starts at 0
B = lambda d: 9.0 + real(d, HOLDS_B)     # segment B starts at 9.0 (after the logo)
LOGO = (3.9, 9.4)

# ---------- helpers ----------
def t_arr(n): return np.arange(n) / SR
def put(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i >= len(buf): return
    sig = sig.copy(); m = min(len(sig), int(SR * .03))
    sig[-m:] *= np.linspace(1, 0, m)          # fade every one-shot's tail to avoid clicks
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain
def env(attack, decay, n):
    t = t_arr(n)
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)
def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), x)
def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)
def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)
def nf(name):
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    return 440 * 2 ** ((names[name[0]] + 12 * (int(name[1:]) + 1) - 69) / 12)

# ---------- instruments ----------
def balafon(f, vel=1.0):
    n = int(SR * 0.9); t = t_arr(n)
    s = (np.sin(2 * np.pi * f * t) * env(.002, .28, n)
         + .38 * np.sin(2 * np.pi * f * 3.93 * t) * env(.001, .045, n)
         + .16 * np.sin(2 * np.pi * f * 2.01 * t) * env(.002, .12, n))
    # the gourd resonators' light buzz
    buzz = bp(rng.standard_normal(n), f * 3, min(f * 6, 16000)) * env(.003, .06, n) * .25
    return (s + buzz) * vel
def djembe(kind, vel=1.0):
    n = int(SR * .5); t = t_arr(n)
    if kind == "bass":
        f = 62 + 30 * np.exp(-t / .03)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.002, .22, n) * vel
    if kind == "tone":
        f = 190 + 40 * np.exp(-t / .02)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.001, .11, n)
        return (s + bp(rng.standard_normal(n), 300, 1500) * env(.001, .03, n) * .5) * vel * .8
    s = bp(rng.standard_normal(n), 1800, 8000) * env(.0015, .045, n) + .4 * np.sin(2 * np.pi * 420 * t) * env(.001, .03, n)
    return s * vel * .7
def shaker(vel=1.0):
    n = int(SR * .09)
    return bp(rng.standard_normal(n), 5000, 11000) * env(.006, .03, n) * vel
def bass(f, length, vel=1.0):
    n = int(SR * length); t = t_arr(n)
    e = np.minimum(1, t / .02) * np.minimum(1, (length - t) / .08)
    return (np.sin(2 * np.pi * f * t) + .25 * np.sin(4 * np.pi * f * t)) * e * vel
def pad(freqs, length, vel=1.0):
    n = int(SR * length); t = t_arr(n)
    s = sum(np.sin(2 * np.pi * f * (1 + d) * t + p) for f in freqs for d, p in [(-.003, 0), (.003, 1.3)])
    e = np.minimum(1, t / 1.2) * np.minimum(1, (length - t) / 1.2)
    return lp(s, 1800) * e * vel / (2 * len(freqs))
def bell(f, vel=1.0, decay=1.6):
    n = int(SR * (decay * 2.2)); t = t_arr(n)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * env(.001, decay / (1 + r * .4), n) for r, a in [(1, 1), (2.76, .45), (5.4, .22), (8.93, .1)])
    return s * vel
def boom(vel=1.0):
    n = int(SR * 1.2); t = t_arr(n)
    f = 46 + 70 * np.exp(-t / .05)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.001, .45, n)
    s += lp(rng.standard_normal(n), 900) * env(.001, .05, n) * .6
    return s * vel
def whoosh(length, vel=1.0):
    n = int(SR * length); t = t_arr(n)
    x = rng.standard_normal(n)
    lo = bp(x, 300, 1200); hi = bp(x, 2500, 7000)
    m = t / length
    e = np.sin(np.pi * m) ** 2
    return (lo * (1 - m) + hi * m) * e * vel
def fly(length, vel=1.0):
    n = int(SR * length); t = t_arr(n)
    f = 210 + 25 * np.sin(2 * np.pi * 1.7 * t) + 12 * np.sin(2 * np.pi * 5.3 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sign(np.sin(ph)) * .5 + np.sin(2 * ph) * .3
    s = bp(s, 180, 3000)
    am = .55 + .45 * np.sin(2 * np.pi * .9 * t) ** 2
    e = np.minimum(1, t / .4) * np.minimum(1, (length - t) / .6)
    return s * am * e * vel

# ---------- the groove ----------
BPM = 100; STEP = 60 / BPM / 4; BAR = STEP * 16
tracks = {k: np.zeros(N) for k in ["bal", "balMin", "drum", "heart", "shk", "bass", "bassMin", "pad", "fx"]}

MAJ = [[(0, "C5"), (2, "E5"), (3, "G5"), (6, "A5"), (8, "G5"), (10, "E5"), (11, "D5"), (14, "C5")],
       [(0, "A4"), (2, "C5"), (3, "E5"), (6, "G5"), (8, "E5"), (10, "D5"), (12, "C5"), (14, "D5")],
       [(0, "G4"), (2, "C5"), (3, "D5"), (6, "E5"), (8, "G5"), (10, "A5"), (11, "G5"), (14, "E5")],
       [(0, "A4"), (2, "C5"), (4, "D5"), (6, "E5"), (8, "D5"), (10, "C5"), (12, "A4"), (14, "G4")]]
MIN = [[(0, "A4"), (6, "C5"), (8, "E4"), (12, "G4")], [(0, "F4"), (6, "A4"), (8, "C5"), (12, "E4")]]
DRUM = {0: "bass", 2: "tone", 3: "tone", 6: "slap", 8: "bass", 10: "tone", 11: "tone", 14: "slap", 15: "slap"}
BASS_MAJ = ["C2", "A1", "G1", "A1"]
BASS_MIN = ["A1", "F1"]

nbars = int(DUR / BAR) + 1
for b in range(nbars):
    t0 = b * BAR
    for st, note in MAJ[b % 4]:
        put(tracks["bal"], t0 + st * STEP, balafon(nf(note), .55 + .15 * (st % 4 == 0)))
        put(tracks["bal"], t0 + st * STEP + .012, balafon(nf(note) * 2, .12))  # octave doubling
    for st, note in MIN[b % 2]:
        put(tracks["balMin"], t0 + st * STEP, balafon(nf(note), .6))
    for st, kind in DRUM.items():
        put(tracks["drum"], t0 + st * STEP, djembe(kind, .9 if st in (0, 8) else .7))
    for st in range(16):
        put(tracks["shk"], t0 + st * STEP, shaker(.9 if st % 4 == 0 else (.55 if st % 2 == 0 else .35)))
    # heartbeat kick for the crisis
    put(tracks["heart"], t0, djembe("bass", 1.0)); put(tracks["heart"], t0 + 2 * STEP, djembe("bass", .7))
    put(tracks["heart"], t0 + 8 * STEP, djembe("bass", 1.0)); put(tracks["heart"], t0 + 10 * STEP, djembe("bass", .7))
    put(tracks["bass"], t0, bass(nf(BASS_MAJ[b % 4]), BAR * .48, .6)); put(tracks["bass"], t0 + 10 * STEP, bass(nf(BASS_MAJ[b % 4]) * 1.5, STEP * 5, .45))
    put(tracks["bassMin"], t0, bass(nf(BASS_MIN[b % 2]), BAR * .9, .6))

# pads: warm C major for the logo, A minor / F for the crisis, C major for the end card
put(tracks["pad"], LOGO[0] - .3, pad([nf("C4"), nf("E4"), nf("G4"), nf("C5")], 6.0, .9))
crisis0, crisis1 = B(3.4), B(7.8)
put(tracks["pad"], crisis0, pad([nf("A3"), nf("C4"), nf("E4")], (crisis1 - crisis0) / 2 + .6, .8))
put(tracks["pad"], crisis0 + (crisis1 - crisis0) / 2 - .6, pad([nf("F3"), nf("A3"), nf("C4")], (crisis1 - crisis0) / 2 + .8, .8))
put(tracks["pad"], B(11.8), pad([nf("C4"), nf("E4"), nf("G4")], DUR - B(11.8), .6))

# ---------- sound effects synced to the picture ----------
fx = tracks["fx"]
put(fx, A(0.7), bell(nf("G5"), .18, 1.0))                        # hook appears
put(fx, A(1.88), boom(1.0))                                        # the stamp hits
put(fx, A(1.88), hp(rng.standard_normal(int(SR * .08)), 1500) * env(.0005, .02, int(SR * .08)) * .8)
put(fx, LOGO[0] - .55, whoosh(1.0, .55))                           # into the logo
put(fx, LOGO[0] + .45, bell(nf("C6"), .35, 2.0)); put(fx, LOGO[0] + .6, bell(nf("G5"), .25, 2.0))
for i, tt in enumerate(np.arange(B(.3), B(1.8), .07)):            # counter ticking up to 180 000
    put(fx, tt, balafon(nf("G6") * (1 + i * .004), .09))
put(fx, B(1.9), bell(nf("E6"), .25, 1.2))                          # "≈100 000 personnes" pill
put(fx, B(3.5), boom(.65))                                         # the background turns dark
put(fx, B(4.8), fly(B(7.5) - B(4.8), .22))                         # flies around the mango
put(fx, B(5.6), boom(.45))                                         # "27 lots interceptés"
pops = ["C5", "D5", "E5", "G5", "A5", "C6"]
for i in range(6):                                                 # derived products pop in
    put(fx, B(8.4 + i * .18) + .05, balafon(nf(pops[i]), .55))
put(fx, B(7.9), whoosh(.6, .35))
put(fx, B(12.75), bell(nf("C6"), .35, 1.8)); put(fx, B(12.8), bell(nf("E6"), .22, 1.8))  # "Le site arrive bientôt"
put(fx, B(13.15), bell(nf("G6"), .16, 1.4))

# ---------- mix: per-section gain curves ----------
def curve(points):
    xs, ys = zip(*points)
    return np.interp(t_arr(N), xs, ys)
c0, c1 = B(3.4), B(7.8)
g = {
    "bal":     curve([(0, .0), (.25, .75), (3.6, .75), (4.1, .2), (8.6, .2), (9.1, .8), (c0, .8), (c0 + .4, 0), (c1 - .3, 0), (c1 + .2, 1.0), (B(11.8), 1.0), (B(12.2), .65), (30.8, .65), (31.9, 0)]),
    "balMin":  curve([(0, 0), (c0, 0), (c0 + .5, .85), (c1 - .4, .85), (c1, 0), (31.9, 0)]),
    "drum":    curve([(0, 0), (.4, .35), (1.85, .35), (1.9, 0), (2.7, 0), (3.0, .35), (3.8, .3), (4.2, 0), (8.5, 0), (9.0, .85), (c0, .85), (c0 + .4, 0), (c1 - .2, 0), (c1 + .2, 1.0), (B(11.8), 1.0), (B(12.2), .55), (30.8, .55), (31.9, 0)]),
    "heart":   curve([(0, 0), (c0 + .2, 0), (c0 + .6, .55), (c1 - .4, .55), (c1, 0), (31.9, 0)]),
    "shk":     curve([(0, 0), (.3, .5), (3.8, .5), (4.2, .15), (8.6, .15), (9.0, .6), (c0, .6), (c0 + .4, .08), (c1, .08), (c1 + .2, .7), (B(11.8), .7), (B(12.2), .4), (30.8, .4), (31.9, 0)]),
    "bass":    curve([(0, 0), (.3, .45), (3.8, .45), (4.2, .2), (8.6, .2), (9.0, .6), (c0, .6), (c0 + .4, 0), (c1, 0), (c1 + .2, .65), (B(11.8), .65), (B(12.2), .45), (30.8, .45), (31.9, 0)]),
    "bassMin": curve([(0, 0), (c0, 0), (c0 + .5, .5), (c1 - .3, .5), (c1, 0), (31.9, 0)]),
    "pad":     curve([(0, .9), (31.0, .9), (31.9, 0)]),
    "fx":      curve([(0, 1), (31.9, 1)]),
}
level = {"bal": .55, "balMin": .55, "drum": .5, "heart": .5, "shk": .12, "bass": .4, "bassMin": .4, "pad": .45, "fx": .7}
mix = sum(tracks[k] * g[k] * level[k] for k in tracks)
# duck the music under the stamp hit
duck = curve([(0, 1), (1.84, 1), (1.9, .45), (2.5, 1), (31.9, 1)])
mix = (mix - tracks["fx"] * g["fx"] * level["fx"]) * duck + tracks["fx"] * level["fx"]
# gentle stereo: balafon a little left, shaker a little right, everything else centred
L = mix + .12 * tracks["bal"] * g["bal"] * level["bal"] - .08 * tracks["shk"] * g["shk"] * level["shk"]
R = mix - .12 * tracks["bal"] * g["bal"] * level["bal"] + .08 * tracks["shk"] * g["shk"] * level["shk"]
st = np.stack([L, R], 1)
st = np.tanh(st * 1.1)                     # soft limiting
st *= .89 / np.max(np.abs(st)) * GAIN      # peak at most about -1 dBFS
fade_in = np.minimum(1, t_arr(N) / .02)[:, None]
wavfile.write("mango_sound.wav", SR, (st * fade_in * 32767).astype(np.int16))
print("events: stamp", A(1.88), "crisis", round(c0, 2), "-", round(c1, 2), "flies", round(B(4.8), 2), "pops", round(B(8.4), 2), "end card", round(B(11.8), 2), "pill", round(B(12.75), 2))
