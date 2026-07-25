# -*- coding: utf-8 -*-
import os, struct, io, sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BIN_PATH = 'EmbeddedSettings.bin'
OUTPUT_PATH = 'EmbeddedSettings.bin'

# Папки игр из трёх директорий
game_folders = {}
for root in [r'c:\Games', r'c:\Games\SmallGames', r'c:\Steam\steamapps\common']:
    if os.path.isdir(root):
        for d in os.listdir(root):
            full = os.path.join(root, d)
            if os.path.isdir(full):
                game_folders[d.lower()] = d

print(f"Найдено папок с играми: {len(game_folders)}")
print("Папки:", sorted(game_folders.values()))

# Читаем текущий EmbeddedSettings.bin
with open(BIN_PATH, 'rb') as f:
    data = f.read()

num = struct.unpack('I', data[:4])[0]
ptr = 4

kept_entries = []
removed_names = []

for i in range(num):
    name_len = struct.unpack('I', data[ptr:ptr+4])[0]; ptr += 4
    name = data[ptr:ptr + name_len*2].decode('utf-16-le'); ptr += name_len*2
    filetime = struct.unpack('Q', data[ptr:ptr+8])[0]; ptr += 8
    content_len = struct.unpack('I', data[ptr:ptr+4])[0]; ptr += 4
    content = data[ptr:ptr + content_len]; ptr += content_len
    
    basename = name[:-6] if name.upper().endswith('.MHOOK') else name
    is_match = basename.lower() in game_folders
    
    if is_match:
        kept_entries.append({'name': name, 'filetime': filetime, 'content': content})
    else:
        removed_names.append(name)

print(f"\nВсего встроено: {num}")
print(f"Оставлено (совпало с папками): {len(kept_entries)}")
print(f"Удалено: {len(removed_names)}")

# Сортируем оставшиеся по времени (новые сверху)
sorted_entries = sorted(kept_entries, key=lambda x: -x['filetime'])

# Записываем новый бинарник
with open(OUTPUT_PATH, 'wb') as f:
    f.write(struct.pack('I', len(sorted_entries)))
    for entry in sorted_entries:
        name_bytes = entry['name'].encode('utf-16-le')
        name_len = len(name_bytes) // 2
        f.write(struct.pack('I', name_len))
        f.write(name_bytes)
        f.write(struct.pack('Q', entry['filetime']))
        f.write(struct.pack('I', len(entry['content'])))
        f.write(entry['content'])

print(f"Записан {OUTPUT_PATH}: {len(sorted_entries)} entries, {os.path.getsize(OUTPUT_PATH)} bytes")

# Сохраняем список удалённых для отчёта
with open('removed_embedded.txt', 'w', encoding='utf-8') as f:
    for name in removed_names:
        f.write(name + '\n')
print(f"Список удалённых сохранён в removed_embedded.txt")
