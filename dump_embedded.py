# -*- coding: utf-8 -*-
import os, struct, sys

# Force UTF-8 for stdout (Windows compatibility)
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

path = 'EmbeddedSettings.bin'
with open(path, 'rb') as f:
    data = f.read()

num = struct.unpack('I', data[:4])[0]
ptr = 4
print(f"Всего встроено: {num}")

# Собираем папки из трёх директорий
game_folders = {}
for root in [r'c:\Games', r'c:\Games\SmallGames', r'c:\Steam\steamapps\common']:
    if os.path.isdir(root):
        for d in os.listdir(root):
            full = os.path.join(root, d)
            if os.path.isdir(full):
                game_folders[d.lower()] = d

matched_names = []
unmatched_names = []

for i in range(num):
    name_len = struct.unpack('I', data[ptr:ptr+4])[0]; ptr += 4
    name = data[ptr:ptr + name_len*2].decode('utf-16-le'); ptr += name_len*2
    filetime = struct.unpack('Q', data[ptr:ptr+8])[0]; ptr += 8
    content_len = struct.unpack('I', data[ptr:ptr+4])[0]; ptr += 4
    ptr += content_len
    
    basename = name[:-6] if name.upper().endswith('.MHOOK') else name
    is_match = basename.lower() in game_folders
    
    if is_match:
        matched_names.append((name, game_folders[basename.lower()]))
    else:
        unmatched_names.append(name)

print(f"Совпало с папками: {len(matched_names)}")
print(f"Не совпало: {len(unmatched_names)}")
print()

print("=== СОВПАВШИЕ (оставить) ===")
for name, folder in matched_names:
    print(f"  {name}  ->  {folder}")

print()
print("=== НЕ СОВПАВШИЕ (удалить) ===")
for name in unmatched_names:
    print(f"  {name}")

