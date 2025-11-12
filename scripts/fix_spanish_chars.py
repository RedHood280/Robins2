#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script rapido para reemplazar tildes y n/N por sus equivalentes sin acento
y eliminar propiedades QSS invalidas (text-shadow y  crea una pequena copia .bak por seguridad.
"""
import os
import io
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EXT = ('.py', '.ui', '.txt', '.md', '.json')

mapping = {
    'a':'a','e':'e','i':'i','o':'o','u':'u',
    'A':'A','E':'E','I':'I','O':'O','U':'U',
    'n':'n','N':'N','u':'u','U':'U'
}

re_accent = re.compile(r'[aeiouAEIOUnNuU]')
re_text_shadow = re.compile(r'text-shadow\s*:\s*[^;]+;?', flags=re.IGNORECASE)
re_transform = re.compile(r'\btransform\s*:\s*[^;]+;?', flags=re.IGNORECASE)

changed_files = []

for dirpath, dirnames, filenames in os.walk(ROOT):
    # Skip virtualenvs or hidden folders if any
    if any(part.startswith('.') for part in dirpath.split(os.sep)):
        continue
    for fn in filenames:
        if not fn.lower().endswith(EXT):
            continue
        path = os.path.join(dirpath, fn)
        try:
            with io.open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception:
            # skip files that can't be read as text
            continue
        orig = text
        if not (re_accent.search(text) or 'text-shadow' in text.lower() or 'transform' in text.lower()):
            continue
        # backup
        bak = path + '.bak'
        try:
            with io.open(bak, 'w', encoding='utf-8') as f:
                f.write(orig)
        except Exception as e:
            print(f"WARN: no pude crear backup para {path}: {e}")
        # replace accented letters
        for k,v in mapping.items():
            text = text.replace(k, v)
        # remove QSS properties
        text = re_text_shadow.sub('', text)
        # remove 