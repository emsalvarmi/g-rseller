#!/usr/bin/env python3
"""Seslendirme metinlerinin motor tarafından nasıl okunacağını (IPA) yazdırır.
Kullanım: python3 farsi/video/ph.py <spec.json>   ya da   python3 farsi/video/ph.py --text "متن"
Her 'voice' alanı için metni ve okunuşunu basar. Okunuş kuralları: farsi/README.md
"""
import json, os, pathlib, sys
import espeakng_loader
from phonemizer.backend.espeak.wrapper import EspeakWrapper
CACHE = pathlib.Path(os.environ.get("FARSI_CACHE", "/tmp/farsi-cache"))
EspeakWrapper.set_library(espeakng_loader.get_library_path())
EspeakWrapper.set_data_path(str(CACHE / "vits-piper-fa_IR-amir-medium/espeak-ng-data"))
from phonemizer import phonemize

def voices(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("voice", "title_voice") and isinstance(v, str):
                yield v
            else:
                yield from voices(v)
    elif isinstance(o, list):
        for v in o:
            yield from voices(v)

texts = [sys.argv[2]] if sys.argv[1] == "--text" else list(voices(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))))
for t in texts:
    print(t)
    print("   ", phonemize(t, language="fa", backend="espeak", preserve_punctuation=True, with_stress=False).replace("q1", "q"))
