#!/usr/bin/env python3
# Restaura archivos desde .bak y corrige encoding mojibake (latin1 -> utf-8) cuando haga falta.
import os
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CANDIDATES = [
    'Robins.py',
    'controllers/main_controller.py',
    'ui/main_window.ui',
    'audio_manager.py',
    'test_nodes.py',
    'README.md',
    'partida_guardada.json'
]

repaired = []
restored = []

for fn in CANDIDATES:
    bak = os.path.join(ROOT, fn + '.bak')
    orig = os.path.join(ROOT, fn)
    if os.path.exists(bak):
        try:
            shutil.copy2(bak, orig)
            restored.append(fn)
        except Exception as e:
            print(f"ERROR al restaurar {fn} desde .bak: {e}")

# ahora corregir encoding si hay mojibake
for fn in restored:
    path = os.path.join(ROOT, fn)
    try:
        with open(path, 'rb') as f:
            data = f.read()
        # try decode as utf-8 first
        try:
            text = data.decode('utf-8')
        except Exception:
            # fallback to latin1 and write utf-8
            text = data.decode('latin-1')
            with open(path, 'w', encoding='utf-8') as fo:
                fo.write(text)
            repaired.append(fn)
            continue
        # if text looks like mojibake (contains sequences like 'Ã' combined with other chars), try latin1
        if 'Ã' in text or 'Â' in text:
            # try decode as latin1 and rewrite as utf-8
            text_latin1 = data.decode('latin-1')
            with open(path, 'w', encoding='utf-8') as fo:
                fo.write(text_latin1)
            repaired.append(fn)
    except Exception as e:
        print(f"ERROR procesando {fn}: {e}")

print('\n--- Resultado ---')
print('Restaurados desde .bak:', len(restored))
for p in restored:
    print(' -', p)
print('Re-codificados (latin1 -> utf-8):', len(repaired))
for p in repaired:
    print(' -', p)
print('\nSe han restaurado archivos y convertido texto a utf-8 cuando se detecto mojibake.')
print('A continuacion ejecutare las pruebas de nodos (test_nodes.py) manualmente.')
