#!/usr/bin/env python3
# Revertir archivos modificados copiando *.bak -> original
import shutil
import os

def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    restored = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith('.bak'):
                bak = os.path.join(dirpath, fn)
                orig = os.path.join(dirpath, fn[:-4])
                try:
                    # make a tiny safety copy of current original before overwrite
                    if os.path.exists(orig):
                        pre = orig + '.pre-revert'
                        if not os.path.exists(pre):
                            shutil.copy2(orig, pre)
                    shutil.copy2(bak, orig)
                    restored.append(os.path.relpath(orig, root))
                except Exception as e:
                    print(f"ERROR al restaurar {bak} -> {orig}: {e}")
    print('\n--- Revertido ---')
    print(f'Archivos restaurados: {len(restored)}')
    for p in restored:
        print(' -', p)

if __name__ == '__main__':
    main()
