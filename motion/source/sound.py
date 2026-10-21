"""Original soundtrack for the mango teaser (31.9 s): "Du verger au port".

Sound design that follows the mango's journey, with an original balafon theme:
  0.0  dawn in an orchard of the North: savanna birds, cicadas, wind in the leaves; the balafon
       theme (the Senufo balafon of the Korhogo region) plays solo
  1.9  the "IMPORT UE SUSPENDU" stamp: the music stops dead on a rubber-stamp hit
  3.9  Maison DOUDJO logo: the theme played as a short sting
  9.0  the sector: the groove starts; mangoes drop into a wooden crate as the counter climbs
 14.0  the crisis: a ship's horn in the port, a container door slams, the theme in minor,
       a heartbeat drum, flies buzzing, a second stamp for the intercepted lots
 21.2  processing: the groove returns; each product has its own sound (knife, pouring juice,
       blender, bubbling jam, ice, mortar and pestle)
 27.2  end card: the theme in full, the birds come back, a chime, fade-out
Everything is synthesised here: no samples and no copyrighted music.
Usage: python3 sound.py [gain]   (writes mango_sound.wav; 0.87 gives about -14 LUFS)
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

GAIN = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
SR = 44100
DUR = 31.9
N = int(SR * DUR)
rng = np.random.default_rng(11)

# ---------- picture timing: the stage's design time -> video time ----------
HOLDS_A = [(2.2, 1.2)]
HOLDS_B = [(2.6, 1.6), (5.0, 0.8), (6.2, 2.0), (10.5, 2.0), (14.0, 1.5)]
def real(d, holds): return d + sum(dur for at, dur in holds if at < d)
A = lambda d: real(d, HOLDS_A)
B = lambda d: 9.0 + real(d, HOLDS_B)
STAMP = A(1.86)                # the stamp lands at 1.86 s, when the picture shakes
LOGO0 = 3.9
SECTOR0 = 9.0
CRISIS0, CRISIS1 = B(3.4), B(7.8)
END0 = B(11.8)

# ---------- DSP helpers ----------
def tt(n): return np.arange(n) / SR
def env(a, d, n):
    t = tt(n); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def flt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)
def noise(n): return rng.standard_normal(n)
def nf(name):
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    acc = 1 if "#" in name else 0
    return 440 * 2 ** ((names[name[0]] + acc + 12 * (int(name[-1]) + 1) - 69) / 12)

class Bus:
    def __init__(self): self.x = np.zeros((N, 2))
    def put(self, start, sig, gain=1.0, pan=0.0):
        if start >= DUR or len(sig) == 0: return
        sig = np.asarray(sig, float)
        if sig.ndim == 1:
            m = min(len(sig), int(SR * .03)); sig = sig.copy(); sig[-m:] *= np.linspace(1, 0, m)
            l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
            sig = np.stack([sig * l, sig * r], 1) * np.sqrt(2)
        i = int(start * SR); j = min(N, i + len(sig))
        if i < 0: sig = sig[-i:]; i = 0
        self.x[i:j] += sig[: j - i] * gain

# ---------- instruments ----------
def balafon(f, vel=1.0, dur=1.1):
    """Wooden bar + gourd resonator + the Senufo membrane buzz."""
    n = int(SR * dur); t = tt(n)
    bar = (np.sin(2 * np.pi * f * t) * env(.0015, .32, n)
           + .42 * np.sin(2 * np.pi * f * 3.98 * t) * env(.0008, .04, n)
           + .18 * np.sin(2 * np.pi * f * 9.1 * t) * env(.0005, .012, n))
    gourd = .35 * np.sin(2 * np.pi * f * t + .6) * (1 - np.exp(-t / .01)) * np.exp(-t / .5)
    body = bar + gourd
    # membrane buzz: a rattle modulated by the note itself
    rattle = flt(noise(n), "band", [min(f * 2.5, 9000), min(f * 7, 15000)])
    buzz = rattle * np.abs(np.sin(2 * np.pi * f * t)) * env(.002, .09, n) * .55
    mallet = flt(noise(int(SR * .006)), "band", [1500, 6000]) * .25
    body[: len(mallet)] += mallet
    return (body + buzz) * vel

def djembe(kind, vel=1.0):
    n = int(SR * .6); t = tt(n)
    if kind == "bass":
        f = 66 + 34 * np.exp(-t / .025)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.0015, .2, n)
        return (s + flt(noise(n), "low", 400) * env(.001, .02, n) * .4) * vel
    if kind == "tone":
        f = 205 + 45 * np.exp(-t / .015)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.001, .09, n) + .3 * np.sin(2 * np.pi * 2.3 * np.cumsum(f) / SR) * env(.001, .04, n)
        return (s + flt(noise(n), "band", [400, 2500]) * env(.001, .025, n) * .5) * vel * .75
    s = flt(noise(n), "band", [1200, 7000]) * env(.001, .04, n) + .35 * np.sin(2 * np.pi * 460 * t) * env(.001, .025, n)
    return s * vel * .7

def dundun(vel=1.0):
    n = int(SR * .7); t = tt(n)
    f = 52 + 40 * np.exp(-t / .03)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.002, .3, n)
    return (s + flt(noise(n), "band", [800, 3000]) * env(.0005, .01, n) * .5) * vel   # stick on skin

def shaker(vel=1.0):
    n = int(SR * .1); return flt(noise(n), "band", [4500, 10000]) * env(.008, .028, n) * vel

def bassnote(f, length, vel=1.0):
    n = int(SR * length); t = tt(n)
    e = np.minimum(1, t / .015) * np.exp(-t / 1.2) * np.minimum(1, (length - t) / .06)
    return (np.sin(2 * np.pi * f * t) + .18 * np.sin(4 * np.pi * f * t)) * e * vel

def pad(freqs, length, vel=1.0, bright=1600):
    n = int(SR * length); t = tt(n); L = np.zeros(n); R = np.zeros(n)
    for f in freqs:
        for d, ph, side in [(-.0035, 0, 0), (.0035, 1.1, 1), (0, 2.2, 2)]:
            w = 2 * np.pi * f * (1 + d) * t + ph
            s = np.sin(w) + .3 * np.sin(2 * w) + .12 * np.sin(3 * w)
            if side == 0: L += s
            elif side == 1: R += s
            else: L += .5 * s; R += .5 * s
    e = np.minimum(1, t / 1.0) * np.minimum(1, (length - t) / 1.0)
    st = np.stack([flt(L, "low", bright), flt(R, "low", bright)], 1)
    return st * e[:, None] * vel / (1.5 * len(freqs))

def bell(f, vel=1.0, decay=1.8):
    n = int(SR * decay * 2.2); t = tt(n)
    return sum(a * np.sin(2 * np.pi * f * r * t) * env(.001, decay / (1 + r * .5), n) for r, a in [(1, 1), (2.76, .4), (5.4, .18), (8.93, .08)]) * vel

# ---------- foley ----------
def birds(length, density=1.0):
    """Savanna dawn: short whistles and trills (weavers, bulbuls)."""
    n = int(SR * length); L = np.zeros(n); R = np.zeros(n)
    tcur = rng.uniform(0, .3)
    while tcur < length - .6:
        kind = rng.integers(3)
        if kind == 0:   # two-note whistle
            seg = []
            for f0, f1, d in [(rng.uniform(2600, 3400), rng.uniform(3000, 3800), .09), (rng.uniform(2200, 2900), rng.uniform(1900, 2500), .12)]:
                m = int(SR * d); tm = tt(m); fr = np.linspace(f0, f1, m)
                seg.append(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * tm / d) ** 2); seg.append(np.zeros(int(SR * .04)))
            s = np.concatenate(seg)
        elif kind == 1:  # trill
            m = int(SR * rng.uniform(.25, .45)); tm = tt(m)
            fr = rng.uniform(3800, 5200) + 600 * np.sin(2 * np.pi * rng.uniform(22, 30) * tm)
            s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * tm / (m / SR)) * (.6 + .4 * np.sin(2 * np.pi * 26 * tm))
        else:            # chirp series
            seg = []
            for _ in range(rng.integers(2, 5)):
                m = int(SR * .045); tm = tt(m); fr = np.linspace(rng.uniform(4200, 5000), rng.uniform(2800, 3400), m)
                seg.append(np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * tm / .045)); seg.append(np.zeros(int(SR * .05)))
            s = np.concatenate(seg)
        i = int(tcur * SR); j = min(n, i + len(s)); p = rng.uniform(-.8, .8)
        g = rng.uniform(.15, .35)
        L[i:j] += s[: j - i] * g * (1 - p) / 2; R[i:j] += s[: j - i] * g * (1 + p) / 2
        tcur += rng.uniform(.25, .7) / density
    return np.stack([L, R], 1)

def cicadas(length):
    n = int(SR * length); t = tt(n)
    out = []
    for f0 in (4300, 5100):
        s = flt(noise(n), "band", [f0 - 400, f0 + 400]) * (.5 + .5 * np.sin(2 * np.pi * 38 * t + rng.uniform(0, 6)) ** 8)
        out.append(s * (.6 + .4 * np.sin(2 * np.pi * .25 * t + rng.uniform(0, 6))))
    return np.stack(out, 1) * .25

def wind(length):
    n = int(SR * length); t = tt(n)
    out = []
    for k in range(2):
        s = flt(noise(n), "band", [250, 1400]) * (.55 + .45 * np.sin(2 * np.pi * .18 * t + k * 1.7))
        leaves = flt(noise(n), "high", 3000) * (np.abs(np.sin(2 * np.pi * .7 * t + k)) ** 6) * .25
        out.append(s * .35 + leaves)
    return np.stack(out, 1)

def stamp(vel=1.0):
    """Rubber stamp on paper over a wooden desk: lift click, thump, paper slap, desk ring."""
    n = int(SR * 1.0); t = tt(n)
    f = 85 + 60 * np.exp(-t / .02)
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.001, .09, n)
    slap = flt(noise(n), "band", [700, 3500]) * env(.0005, .025, n) * .9
    desk = sum(a * np.sin(2 * np.pi * fr * t) * env(.001, dc, n) for fr, a, dc in [(180, .35, .12), (410, .2, .07), (930, .1, .04)])
    s = thump + slap + desk
    click = np.zeros(int(SR * .07)); click[:int(SR * .004)] = flt(noise(int(SR * .004)), "high", 3000) * .3
    return np.concatenate([click, s]) * vel

def crate_drop(pitch=1.0, vel=1.0):
    """A mango falling into a wooden crate: soft fruit thud + wood knock."""
    n = int(SR * .35); t = tt(n)
    f = (95 + 50 * np.exp(-t / .015)) * pitch
    fruit = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.002, .06, n)
    wood = sum(a * np.sin(2 * np.pi * fr * pitch * t) * env(.0008, dc, n) for fr, a, dc in [(320, .45, .06), (690, .3, .04), (1240, .15, .025)])
    return (fruit + wood) * vel

def ship_horn(length=2.6, vel=1.0):
    n = int(SR * length); t = tt(n)
    f = 73.4 * (1 + .004 * np.sin(2 * np.pi * 4.5 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(k * ph) / k ** .9 for k in range(1, 18))
    s += .6 * sum(np.sin(k * ph * 1.5) / k for k in range(1, 10))   # the fifth: a two-tone horn
    s = flt(s, "low", 900)
    e = np.minimum(1, t / .35) * np.minimum(1, (length - t) / .5)
    return s * e * vel * .12

def container_slam(vel=1.0):
    n = int(SR * 2.2); t = tt(n)
    modes = [(96, 1, .9), (151, .7, .7), (233, .55, .5), (389, .4, .35), (577, .3, .25), (911, .2, .18), (1433, .12, .12)]
    s = sum(a * np.sin(2 * np.pi * fr * t + rng.uniform(0, 6)) * env(.001, dc, n) for fr, a, dc in modes)
    s += flt(noise(n), "low", 1500) * env(.0005, .04, n) * .8
    return s * vel * .6

def heartbeat(vel=1.0):
    n = int(SR * .5); t = tt(n)
    f = 48 + 20 * np.exp(-t / .03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.004, .12, n) * vel

def fly(length, vel=1.0, base=210):
    n = int(SR * length); t = tt(n)
    f = base + 25 * np.sin(2 * np.pi * 1.7 * t) + 12 * np.sin(2 * np.pi * 5.3 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = flt(np.sign(np.sin(ph)) * .5 + np.sin(2 * ph) * .3, "band", [180, 3000])
    am = .55 + .45 * np.sin(2 * np.pi * .9 * t) ** 2
    e = np.minimum(1, t / .4) * np.minimum(1, (length - t) / .6)
    pan = np.sin(2 * np.pi * .35 * t)      # the fly circles: it moves left and right
    return np.stack([s * am * e * (1 - pan) / 2, s * am * e * (1 + pan) / 2], 1) * vel * 1.4

def whoosh(length, vel=1.0):
    n = int(SR * length); t = tt(n); x = noise(n); m = t / length
    s = flt(x, "band", [300, 1200]) * (1 - m) + flt(x, "band", [2500, 7000]) * m
    return s * np.sin(np.pi * m) ** 2 * vel

# product foley for the processing section
def knife(vel=1.0):
    n = int(SR * .22); t = tt(n)
    sweep = flt(noise(n), "band", [2500, 9000]) * np.sin(np.pi * t / .22) ** 3
    tick = np.zeros(n); tick[int(SR * .19):int(SR * .195)] = 1
    return (sweep * .8 + flt(tick, "band", [800, 3000]) * 2) * vel
def pour(vel=1.0):
    n = int(SR * .5); t = tt(n); s = flt(noise(n), "band", [400, 2200]) * .25 * np.sin(np.pi * t / .5)
    for _ in range(16):
        st = rng.uniform(0, .42); m = int(SR * .03); tm = tt(m); f = np.linspace(rng.uniform(380, 700), rng.uniform(800, 1300), m)
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tm / .01); i = int(st * SR); s[i:i + m] += b * .4
    return s * vel
def blender(vel=1.0):
    n = int(SR * .4); t = tt(n); f = 140 + 120 * np.minimum(1, t / .15)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = flt(np.sign(np.sin(ph)) + .5 * np.sign(np.sin(3.01 * ph)), "band", [150, 2500]) * .25
    return s * np.sin(np.pi * t / .4) * vel
def bubbles(vel=1.0):
    n = int(SR * .45); s = np.zeros(n)
    for _ in range(9):
        st = rng.uniform(0, .38); m = int(SR * .05); tm = tt(m); f = np.linspace(rng.uniform(160, 260), rng.uniform(320, 480), m)
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tm / .05); i = int(st * SR); s[i:i + m] += b * .45
    return s * vel
def ice(vel=1.0):
    n = int(SR * .5); t = tt(n); s = np.zeros(n)
    for st in (0, .07, .16):
        m = int(SR * .3); tm = tt(m); i = int(st * SR)
        c = sum(a * np.sin(2 * np.pi * fr * tm) * np.exp(-tm / dc) for fr, a, dc in [(2650, 1, .05), (4120, .6, .03), (5980, .4, .02)])
        s[i:i + m] += c[: n - i] * (.5 if st else .7)
    return s * vel
def pestle(vel=1.0):
    n = int(SR * .35); t = tt(n)
    s = np.sin(2 * np.pi * (110 + 50 * np.exp(-t / .01)) * t) * env(.001, .07, n)
    s += sum(a * np.sin(2 * np.pi * fr * t) * env(.001, dc, n) for fr, a, dc in [(260, .4, .08), (540, .25, .05)])
    s += flt(noise(n), "band", [600, 2500]) * env(.001, .02, n) * .3
    return s * vel

# ---------- reverb ----------
def reverb_ir(length=2.2, damp=4500):
    n = int(SR * length); t = tt(n)
    e = np.exp(-t / (length / 6.5))
    ir = np.stack([flt(noise(n), "low", damp) * e, flt(noise(n), "low", damp) * e], 1)
    ir[: int(SR * .012)] = 0          # pre-delay
    return ir / np.sqrt(np.sum(ir ** 2) / 2)
def apply_reverb(x, ir, wet):
    y = np.stack([fftconvolve(x[:, 0], ir[:, 0])[:N], fftconvolve(x[:, 1], ir[:, 1])[:N]], 1)
    return y * wet

# ---------- buses ----------
bal, perc, low, padb, amb, fx, theme = (Bus() for _ in range(7))

# The mango theme (C major pentatonic) and its minor version (A minor pentatonic), in 8th notes
THEME = [("E5", 0), ("G5", 1), ("A5", 2), ("G5", 3), ("E5", 4), ("D5", 5), ("C5", 6),
         ("D5", 8), ("E5", 9), ("G5", 10), ("E5", 11), ("D5", 12), ("C5", 13), ("A4", 14)]
THEME_MIN = [("E5", 0), ("C5", 2), ("A4", 4), ("G4", 6), ("A4", 8), ("C5", 10), ("B4", 12), ("A4", 14)]
BPM = 100; E8 = 60 / BPM / 2; S16 = E8 / 2; BAR = S16 * 16
def play_theme(bus, t0, notes, vel=.6, octave=1.0, swing=0.0, pan=-.15):
    for name, step in notes:
        tt0 = t0 + step * E8 + (swing * E8 if step % 2 else 0)
        bus.put(tt0, balafon(nf(name) * octave, vel), 1, pan)
        bus.put(tt0 + .011, balafon(nf(name) * octave * 2, vel * .18), 1, -pan)

OSTI = [[(0, "C5"), (2, "E5"), (3, "G5"), (6, "A5"), (8, "G5"), (10, "E5"), (11, "D5"), (14, "C5")],
        [(0, "A4"), (2, "C5"), (3, "E5"), (6, "G5"), (8, "E5"), (10, "D5"), (12, "C5"), (14, "D5")],
        [(0, "G4"), (2, "C5"), (3, "D5"), (6, "E5"), (8, "G5"), (10, "A5"), (11, "G5"), (14, "E5")],
        [(0, "A4"), (2, "C5"), (4, "D5"), (6, "E5"), (8, "D5"), (10, "C5"), (12, "A4"), (14, "G4")]]
DRUM = {0: "bass", 2: "tone", 3: "tone", 6: "slap", 8: "bass", 10: "tone", 11: "tone", 14: "slap", 15: "slap"}
DUN = [0, 3, 6, 10]
BASSLINE = ["C2", "A1", "G1", "A1"]

def groove(t0, t1, intensity=1.0, bright=False):
    b = 0
    while t0 + b * BAR < t1:
        tb = t0 + b * BAR
        for st, note in OSTI[b % 4]:
            if tb + st * S16 < t1:
                bal.put(tb + st * S16, balafon(nf(note) * (2 if bright and st % 4 == 2 else 1), .42 * intensity), 1, .35)
        for st, kind in DRUM.items():
            if tb + st * S16 < t1: perc.put(tb + st * S16, djembe(kind, (.9 if st in (0, 8) else .65) * intensity), 1, -.25 if kind != "bass" else 0)
        for st in DUN:
            if tb + st * S16 < t1: perc.put(tb + st * S16, dundun(.7 * intensity), 1, .1)
        for st in range(16):
            if tb + st * S16 < t1: perc.put(tb + st * S16, shaker((.8 if st % 4 == 0 else .45 if st % 2 == 0 else .28) * intensity), .5, .45)
        if tb < t1:
            low.put(tb, bassnote(nf(BASSLINE[b % 4]), min(BAR * .55, t1 - tb), .7 * intensity))
            if tb + 10 * S16 < t1: low.put(tb + 10 * S16, bassnote(nf(BASSLINE[b % 4]) * 1.5, min(S16 * 5, t1 - tb - 10 * S16), .5 * intensity))
        b += 1

# --- 0.0-3.9  dawn in the orchard, the theme solo, then the stamp ---
amb.put(0, birds(9.8, 1.2), .9)
amb.put(0, cicadas(9.8), .5)
amb.put(0, wind(9.8), .5)
padb.put(0, pad([nf("C3"), nf("G3"), nf("E4")], STAMP + .25, .55, 1100))
play_theme(theme, .25, THEME[:7], vel=.55)            # first half of the theme...
fx.put(STAMP - .07, stamp(1.3), 1, 0)                   # ...cut off by the stamp
fx.put(STAMP, container_slam(.45), 1, .2)
padb.put(STAMP + .1, pad([nf("C3"), nf("F#3"), nf("C4")], 2.6, .35, 700))   # an uneasy chord under the question
# --- 3.9-9.0  logo sting ---
fx.put(LOGO0 - .6, whoosh(1.0, .5))
play_theme(theme, LOGO0 + .35, THEME, vel=.55, octave=1.0)
padb.put(LOGO0 + .2, pad([nf("C3"), nf("E3"), nf("G3"), nf("C4"), nf("E4")], 5.0, .75))
fx.put(LOGO0 + .35, bell(nf("C6"), .22, 2.2), 1, .3)
low.put(LOGO0 + .35, bassnote(nf("C2"), 3.0, .55))
# --- 9.0-14.0  the sector: groove, crates filling up ---
groove(SECTOR0, CRISIS0 + .1)
for i, ttk in enumerate(np.arange(B(.3), B(1.8), .085)):
    fx.put(ttk, crate_drop(rng.uniform(.9, 1.15), .35 + .25 * i / 18), 1, rng.uniform(-.5, .5))
play_theme(theme, B(1.9), THEME[7:], vel=.45, octave=2.0, pan=.2)     # a bright answer on the "≈100 000 personnes" pill
# --- 14.0-21.2  the crisis at the port ---
fx.put(CRISIS0 - .1, ship_horn(3.0, 1.0), 1, -.1)
fx.put(B(3.9) + .1, container_slam(.9), 1, .25)                       # "Depuis le 1er août 2026"
padb.put(CRISIS0, pad([nf("A2"), nf("E3"), nf("C4")], (CRISIS1 - CRISIS0) / 2 + .8, .8, 900))
padb.put((CRISIS0 + CRISIS1) / 2 - .4, pad([nf("F2"), nf("C3"), nf("A3")], (CRISIS1 - CRISIS0) / 2 + .6, .8, 900))
hb = CRISIS0 + .9
while hb < CRISIS1 - .4:
    perc.put(hb, heartbeat(1.0)); perc.put(hb + .28, heartbeat(.6)); hb += 1.2
play_theme(theme, CRISIS0 + 1.2, THEME_MIN, vel=.5, octave=.5, pan=-.3)
play_theme(theme, CRISIS0 + 4.0, THEME_MIN[:4], vel=.4, octave=.5, pan=-.3)
fx.put(B(4.8), fly(B(7.5) - B(4.8), .3), 1)
fx.put(B(5.2), fly(B(7.5) - B(5.2), .2, 247), 1)
fx.put(B(5.6) - .05, stamp(.8), 1, .15)                                   # "27 lots interceptés"
low.put(CRISIS0, bassnote(nf("A1"), 3.5, .5)); low.put((CRISIS0 + CRISIS1) / 2, bassnote(nf("F1"), 3.5, .5))
# --- 21.2-27.2  processing: the groove returns, each product has its sound ---
fx.put(CRISIS1 - .45, whoosh(.6, .35))
groove(CRISIS1, END0 + .2, 1.0, bright=True)
for i, f in enumerate([knife, pour, blender, bubbles, ice, pestle]):
    ttp = B(8.4 + i * .18)
    fx.put(ttp, f(.9), 1, (-.6 + i * .24))
    theme.put(ttp, balafon(nf(["C5", "D5", "E5", "G5", "A5", "C6"][i]), .35), 1, (-.6 + i * .24))
# --- 27.2-31.9  end card: the theme in full, the orchard again ---
amb.put(END0 - .3, birds(DUR - END0 + .3, .9), .7)
amb.put(END0 - .3, wind(DUR - END0 + .3), .35)
play_theme(theme, END0 + .1, THEME, vel=.6, swing=.12)
padb.put(END0, pad([nf("C3"), nf("G3"), nf("E4"), nf("A4")], DUR - END0, .7))
low.put(END0 + .1, bassnote(nf("C2"), 3.5, .6))
fx.put(B(12.75), bell(nf("C6"), .3, 2.0), 1, -.2); fx.put(B(12.8), bell(nf("G6"), .18, 2.0), 1, .2)
theme.put(END0 + 2.4 * 1.0 + 1.2, balafon(nf("C5"), .5, 2.5), 1, 0)       # final note, left to ring

# ---------- mix ----------
def curve(points):
    xs, ys = zip(*points); return np.interp(tt(N), xs, ys)[:, None]
music_cut = curve([(0, 1), (STAMP - .02, 1), (STAMP, 0), (LOGO0 - .4, 0), (LOGO0 - .1, 1), (DUR, 1)])
amb_g = curve([(0, 0), (.4, 1), (STAMP, 1), (STAMP + .3, .45), (LOGO0, .45), (LOGO0 + 1.5, 0), (END0 - .5, 0), (END0 + .5, .8), (DUR, .8)])
mix = (theme.x * 1.0 + bal.x * .75) * music_cut
mix += perc.x * .7 + low.x * .55 + padb.x * .5
mix += amb.x * amb_g * .55
mix += fx.x * .85

# reverb: more on the balafon theme and the pads, a little on the rest
ir = reverb_ir()
send = theme.x * music_cut * .5 + bal.x * music_cut * .2 + padb.x * .35 + fx.x * .18 + perc.x * .08
mix += apply_reverb(send, ir, .35)

# gentle bus compression (RMS, 3:1 above -18 dBFS) then a soft limiter
rms = np.sqrt(flt(np.mean(mix ** 2, 1), "low", 8) .clip(1e-12))
thr = 10 ** (-18 / 20); gr = np.where(rms > thr, (thr * (rms / thr) ** (1 / 3)) / rms, 1.0)
mix *= gr[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) / np.tanh(1.6)
mix *= .89 * GAIN
fade = np.minimum(1, tt(N) / .03) * np.clip((DUR - tt(N)) / .9, 0, 1)
mix *= fade[:, None]
wavfile.write("mango_sound.wav", SR, (mix * 32767).astype(np.int16))
print("stamp", round(STAMP, 2), "crisis", round(CRISIS0, 2), round(CRISIS1, 2), "end", round(END0, 2))
