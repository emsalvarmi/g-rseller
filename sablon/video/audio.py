# Usage: python3 audio.py timeline.json out.wav
# Builds an original music bed and sound effects from the video's timeline (no samples, no copyrighted material).
import json, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

tl = json.load(open(sys.argv[1], encoding='utf-8'))
OUT = sys.argv[2]
SR = 44100
DUR = float(tl['duration'])
N = int(SR * DUR) + 1
rng = np.random.default_rng(7)
mix = np.zeros(N)
hats = np.zeros(N)

def t_of(n): return np.arange(n) / SR
def place(buf, sig, at, gain=1.0):
    i = int(max(0, at) * SR); j = min(N, i + len(sig))
    if i < N: buf[i:j] += sig[: j - i] * gain
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)

def kick(d=0.35):
    t = t_of(int(SR * d)); f = 45 + 75 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def hat(d=0.06):
    n = int(SR * d); return hp(rng.standard_normal(n), 7000) * np.exp(-t_of(n) * 70)
def boom(d=0.9, f0=70, f1=38):
    t = t_of(int(SR * d)); f = f1 + (f0 - f1) * np.exp(-t * 6)
    click = hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 120) * 0.5
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5) + click
def blip(freq=1200, d=0.12, decay=35):
    t = t_of(int(SR * d)); return np.sin(2 * np.pi * freq * t) * np.exp(-t * decay)
def chime(d=1.4):
    t = t_of(int(SR * d))
    s = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(880, 1.0), (1108.7, 0.8), (1318.5, 0.6), (1760, 0.25)])
    return s * np.exp(-t * 3.2) / 2.6
def whoosh(d=0.45):
    n = int(SR * d); t = t_of(n); env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2; w = np.clip(t / d, 0, 1)
    return (bp(rng.standard_normal(n), 300, 1500) * (1 - w) + bp(rng.standard_normal(n), 1500, 6000) * w) * env
def siren(d=0.9):
    t = t_of(int(SR * d)); f = np.where((t * 2.5) % 1 < 0.5, 720, 960)
    return lp(np.sin(2 * np.pi * np.cumsum(f) / SR), 2500) * np.minimum(1, t * 8) * np.minimum(1, (d - t) * 8)
def tick():
    n = int(SR * 0.03); return bp(rng.standard_normal(n), 1500, 3500) * np.exp(-t_of(n) * 160)
def pad(freqs, d, gain=1.0):
    t = t_of(int(SR * d)); s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6): s += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6.28))
    env = np.minimum(1, t / 0.35) * np.minimum(1, (d - t) / 0.35)
    return lp(s, 1800) * env * gain / (2 * len(freqs))

# windows
quiz = [tuple(w) for w in tl.get('quizWins', [])]
groove, cur = [], 0.0
for a, b in sorted(quiz):
    if a > cur: groove.append((cur, a))
    cur = max(cur, b)
if cur < DUR: groove.append((cur, DUR))

BEAT = 0.6
CH = [(110.0, [220, 261.63, 329.63]), (87.31, [174.61, 220, 261.63]), (130.81, [196, 261.63, 329.63]), (98.0, [196, 246.94, 293.66])]
for a, b in groove:
    k = a
    while k < b - 0.05:
        place(mix, kick(), k, 0.5); place(hats, hat(), k + BEAT / 2, 0.10); k += BEAT
    k, i = a, 0
    while k < b - 0.1:
        root, tri = CH[i % 4]; d = min(BEAT * 4, b - k)
        place(mix, pad(tri, d, 0.55), k)
        tb = t_of(int(SR * d))
        place(mix, lp(np.sin(2 * np.pi * root * tb) * np.minimum(1, tb / 0.02) * np.exp(-((tb % BEAT) * 3.0)), 400) * 0.35, k)
        k += BEAT * 4; i += 1
for a, b in quiz:
    d = b - a
    place(mix, pad([164.81, 207.65, 246.94], d, 0.6), a)
    tb = t_of(int(SR * d)); place(mix, lp(np.sin(2 * np.pi * 41.2 * tb), 200) * 0.3 * np.minimum(1, tb / 0.5), a)
    k = a + 0.2
    while k < b - 1.6: place(mix, tick(), k, 0.3); k += 0.5

for e in tl['events']:
    t, ty = e['t'], e['type']
    if ty == 'whoosh': place(mix, whoosh(), t, 0.22)
    elif ty == 'boom': place(mix, boom(), t, 0.75)
    elif ty == 'thud': place(mix, boom(0.45, 115, 58), t, 0.4)
    elif ty == 'blip': place(mix, blip(1320, 0.12, 30), t, 0.16)
    elif ty == 'pop': place(mix, blip(880, 0.18, 22), t, 0.12)
    elif ty == 'chime': place(mix, chime(1.0 if e.get('soft') else 1.4), t, 0.18 if e.get('soft') else 0.32)
    elif ty == 'count': place(mix, blip(1000, 0.14, 25), t, 0.3)
    elif ty == 'siren': place(mix, siren(e.get('d', 0.9)), t, 0.06)
    elif ty == 'glitch':
        k = t
        while k < t + e.get('d', 1.0):
            n = int(SR * 0.04)
            g = np.sign(np.sin(2 * np.pi * rng.uniform(200, 900) * t_of(n))) * np.exp(-t_of(n) * 60)
            place(mix, g, k, 0.05); k += 0.09

fade = np.ones(N); fs = int(max(0, DUR - 1.5) * SR); fade[fs:] = np.linspace(1, 0, N - fs)
st = np.stack([(mix + hats * 0.8) * fade, (mix + hats * 1.2) * fade], axis=1)
st = np.tanh(st * 1.3) / np.tanh(1.3)
st = st / max(1e-9, np.max(np.abs(st))) * 0.89
wavfile.write(OUT, SR, (st * 32767).astype(np.int16))
print('audio', round(DUR, 2), 's')
