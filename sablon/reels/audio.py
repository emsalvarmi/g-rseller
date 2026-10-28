# Synthesizes an original music bed and sound effects for the Reel (no samples, no copyrighted material).
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
DUR = 32.5
N = int(SR * DUR)
rng = np.random.default_rng(7)
mix = np.zeros(N)
hats = np.zeros(N)

def t_of(n):
    return np.arange(n) / SR

def place(buf, sig, at, gain=1.0):
    i = int(at * SR)
    j = min(N, i + len(sig))
    if i < N:
        buf[i:j] += sig[: j - i] * gain

def lp(x, f, order=2):
    return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)

def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)

def kick(dur=0.35):
    t = t_of(int(SR * dur))
    f = 45 + 75 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9)

def hat(dur=0.06):
    n = int(SR * dur)
    return hp(rng.standard_normal(n), 7000) * np.exp(-t_of(n) * 70)

def boom(dur=0.9, f0=70, f1=38):
    t = t_of(int(SR * dur))
    f = f1 + (f0 - f1) * np.exp(-t * 6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    click = hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 120) * 0.5
    return (np.sin(ph) * np.exp(-t * 4.5) + click)

def blip(freq=1200, dur=0.12, decay=35):
    t = t_of(int(SR * dur))
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * decay)

def chime(dur=1.4):
    t = t_of(int(SR * dur))
    s = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(880, 1.0), (1108.7, 0.8), (1318.5, 0.6), (1760, 0.25)])
    return s * np.exp(-t * 3.2) / 2.6

def whoosh(dur=0.45):
    n = int(SR * dur)
    t = t_of(n)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    lo = bp(rng.standard_normal(n), 300, 1500)
    hi = bp(rng.standard_normal(n), 1500, 6000)
    w = np.clip(t / dur, 0, 1)
    return (lo * (1 - w) + hi * w) * env

def siren(dur=0.9):
    t = t_of(int(SR * dur))
    f = np.where((t * 2.5) % 1 < 0.5, 720, 960)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return lp(s, 2500) * np.minimum(1, t * 8) * np.minimum(1, (dur - t) * 8)

def tick():
    n = int(SR * 0.03)
    return bp(rng.standard_normal(n), 1500, 3500) * np.exp(-t_of(n) * 160)

def pad_chord(freqs, dur, gain=1.0):
    t = t_of(int(SR * dur))
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6):
            s += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6.28))
    env = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.35)
    return lp(s, 1800) * env * gain / (2 * len(freqs))

# ---- music bed ----
BEAT = 0.6  # 100 BPM
groove = [(0.0, 13.3), (19.5, 31.4)]
for a, b in groove:
    k = a
    while k < b - 0.05:
        place(mix, kick(), k, 0.55)
        place(hats, hat(), k + BEAT / 2, 0.10)
        k += BEAT

# chord progression Am F C G (4 beats each)
A, F, C, G, E = (110.0, [220, 261.63, 329.63]), (87.31, [174.61, 220, 261.63]), (130.81, [196, 261.63, 329.63]), (98.0, [196, 246.94, 293.66]), (82.41, [164.81, 207.65, 246.94])
prog_chords = [A, F, C, G]
def play_progression(a, b):
    k, i = a, 0
    while k < b - 0.1:
        root, tri = prog_chords[i % 4]
        d = min(BEAT * 4, b - k)
        place(mix, pad_chord(tri, d, 0.55), k)
        tb = t_of(int(SR * d))
        bass = np.sin(2 * np.pi * root * tb) * np.minimum(1, tb / 0.02) * np.exp(-((tb % BEAT) * 3.0))
        place(mix, lp(bass, 400) * 0.35, k)
        k += BEAT * 4; i += 1
play_progression(0.0, 13.3)
play_progression(19.5, 31.4)

# tension (quiz): drone on E with ticking clock
place(mix, pad_chord(E[1], 6.2, 0.6), 13.3)
tdr = t_of(int(SR * 6.2))
place(mix, lp(np.sin(2 * np.pi * 41.2 * tdr), 200) * 0.30 * np.minimum(1, tdr / 0.5), 13.3)
k = 13.5
while k < 18.6:
    place(mix, tick(), k, 0.35)
    k += 0.5
for at in (15.6, 16.6, 17.6):
    place(mix, blip(1000, 0.14, 25), at, 0.30)

# ---- sound effects ----
for at in (3.5, 5.6, 7.65, 9.7, 13.3, 25.7, 29.5):
    place(mix, whoosh(), at - 0.2, 0.22)
place(mix, siren(0.95), 1.4, 0.06)
place(mix, siren(0.8), 11.55, 0.05)
place(mix, boom(), 2.32, 0.75)      # ÇALINTI stamp
place(mix, boom(0.7, 90, 45), 11.6, 0.6)  # police tape
place(mix, boom(1.1, 60, 32), 18.6, 0.8)  # countdown end
place(mix, chime(), 19.6, 0.32)     # answer
for at in (6.0, 6.3, 6.6):
    place(mix, blip(1320, 0.12, 30), at, 0.16)
place(mix, boom(0.4, 120, 60), 6.95, 0.35)   # SORUN YOK stamp
place(mix, boom(0.5, 110, 55), 8.15, 0.45)   # notary seal
place(mix, blip(880, 0.2, 18), 22.5, 0.14)   # 'Üstelik' card
place(mix, chime(1.0), 30.8, 0.18)           # follow button
# glitch during VIN scramble
k = 10.4
while k < 11.3:
    n = int(SR * 0.04)
    g = np.sign(np.sin(2 * np.pi * rng.uniform(200, 900) * t_of(n))) * np.exp(-t_of(n) * 60)
    place(mix, g, k, 0.05)
    k += 0.09

# ---- master ----
fade = np.ones(N)
fs, fe = int(31.0 * SR), N
fade[fs:fe] = np.linspace(1, 0, fe - fs)
left = (mix + hats * 0.8) * fade
right = (mix + hats * 1.2) * fade
st = np.stack([left, right], axis=1)
st = np.tanh(st * 1.3) / np.tanh(1.3)
st = st / np.max(np.abs(st)) * 0.89
wavfile.write('music.wav', SR, (st * 32767).astype(np.int16))
print('wrote music.wav', DUR, 's')
