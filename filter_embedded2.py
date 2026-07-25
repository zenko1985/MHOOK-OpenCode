# -*- coding: utf-8 -*-
import os, struct, sys, re, io
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BIN_PATH = 'EmbeddedSettings.bin'
OUTPUT_PATH = 'EmbeddedSettings.bin'

game_folders = {}
for root in [r'c:\Games', r'c:\Games\SmallGames', r'c:\Steam\steamapps\common']:
    if os.path.isdir(root):
        for d in os.listdir(root):
            full = os.path.join(root, d)
            if os.path.isdir(full):
                key = d.strip().lower()
                game_folders[key] = d

print(f"Найдено папок с играми: {len(game_folders)}")

sorted_folders = sorted(game_folders.items(), key=lambda x: -len(x[0]))

def strip_suffix(name):
    return re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()

def prefix_match(short, long):
    if not long.startswith(short):
        return False
    rest = long[len(short):]
    at_boundary = len(rest) == 0 or rest[0] in ' (.-'
    if len(short) < 4:
        return at_boundary and len(short) == len(long)
    return at_boundary

def match_config(config_name):
    cn_lower = config_name.lower().strip()
    
    for fkey, fname in sorted_folders:
        # 1. Exact match
        if cn_lower == fkey:
            return fname
        # 2. Strip suffix then exact match
        base = strip_suffix(cn_lower)
        if base == fkey:
            return fname
        # 3. Config starts with folder
        if prefix_match(fkey, cn_lower):
            return fname
        # 4. Folder starts with config
        if len(cn_lower) >= 2 and prefix_match(cn_lower, fkey):
            return fname
        # 5. Stripped config starts with folder
        if base != cn_lower and prefix_match(fkey, base):
            return fname
        # 6. Folder starts with stripped config
        if base != cn_lower and len(base) >= 2 and prefix_match(base, fkey):
            return fname
    
    return None

with open(BIN_PATH, 'rb') as f:
    data = f.read()

num = struct.unpack('I', data[:4])[0]
ptr = 4

kept = []
removed = []

for i in range(num):
    name_len = struct.unpack('I', data[ptr:ptr+4])[0]; ptr += 4
    name = data[ptr:ptr + name_len*2].decode('utf-16-le'); ptr += name_len*2
    filetime = struct.unpack('Q', data[ptr:ptr+8])[0]; ptr += 8
    content_len = struct.unpack('I', data[ptr:ptr+4])[0]; ptr += 4
    content = data[ptr:ptr + content_len]; ptr += content_len
    
    basename = name[:-6] if name.upper().endswith('.MHOOK') else name
    matched_folder = match_config(basename)
    
    if matched_folder:
        kept.append({'name': name, 'filetime': filetime, 'content': content, 'folder': matched_folder})
    else:
        removed.append(name)

print(f"\nВсего: {num}, оставлено: {len(kept)}, удалено: {len(removed)}")

sorted_kept = sorted(kept, key=lambda x: -x['filetime'])
with open(OUTPUT_PATH, 'wb') as f:
    f.write(struct.pack('I', len(sorted_kept)))
    for e in sorted_kept:
        nb = e['name'].encode('utf-16-le')
        f.write(struct.pack('I', len(nb)//2))
        f.write(nb)
        f.write(struct.pack('Q', e['filetime']))
        f.write(struct.pack('I', len(e['content'])))
        f.write(e['content'])

print(f"Записан {OUTPUT_PATH}: {len(sorted_kept)} entries, {os.path.getsize(OUTPUT_PATH)} bytes")

with open('removed_embedded.txt', 'w', encoding='utf-8') as f:
    for n in removed:
        f.write(n + '\n')

print("\n=== ОСТАВЛЕННЫЕ ===")
for e in sorted_kept:
    print(f"  {e['name']}  ->  {e['folder']}")

print(f"\n=== ПЕРВЫЕ 30 УДАЛЁННЫХ ===")
for n in removed[:30]:
    print(f"  {n}")
