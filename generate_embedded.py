# -*- coding: utf-8 -*-
import os
import struct

SOURCE_DIR = r"C:\Programs\mhook"
EXISTING_BIN = "EmbeddedSettings.bin"
OUTPUT_FILE = "EmbeddedSettings.bin"

def unix_to_filetime(ts):
    EPOCH_AS_FILETIME = 116444736000000000
    return int(ts * 10000000) + EPOCH_AS_FILETIME

def read_existing_bin(path):
    entries = {}
    if not os.path.exists(path):
        return entries
    with open(path, 'rb') as f:
        data = f.read()
    if len(data) < 4:
        return entries
    num_files = struct.unpack('I', data[:4])[0]
    ptr = 4
    for i in range(num_files):
        if ptr + 4 > len(data): break
        name_len = struct.unpack('I', data[ptr:ptr+4])[0]
        ptr += 4
        if ptr + name_len * 2 > len(data): break
        name = data[ptr:ptr + name_len * 2].decode('utf-16-le')
        ptr += name_len * 2
        if ptr + 8 > len(data): break
        filetime = struct.unpack('Q', data[ptr:ptr+8])[0]
        ptr += 8
        if ptr + 4 > len(data): break
        content_len = struct.unpack('I', data[ptr:ptr+4])[0]
        ptr += 4
        if ptr + content_len > len(data): break
        content = data[ptr:ptr + content_len]
        ptr += content_len
        key = name.lower()
        if key not in entries:
            entries[key] = {'name': name, 'filetime': filetime, 'content': content}
    return entries

def main():
    entries = read_existing_bin(EXISTING_BIN)
    print(f"Existing entries loaded: {len(entries)}")
    dir_files = []
    for filename in os.listdir(SOURCE_DIR):
        if not filename.lower().endswith('.mhook'):
            continue
        filepath = os.path.join(SOURCE_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        stat_info = os.stat(filepath)
        basename = filename[:-6]
        normalized_name = basename + '.MHOOK'
        with open(filepath, 'rb') as fp:
            content = fp.read()
        filetime = unix_to_filetime(stat_info.st_mtime)
        dir_files.append({'name': normalized_name, 'filetime': filetime, 'content': content})
    print(f"Files found in directory: {len(dir_files)}")
    updated_count = 0
    new_count = 0
    for f in dir_files:
        key = f['name'].lower()
        if key in entries:
            updated_count += 1
        else:
            new_count += 1
        entries[key] = f
    print(f"Updated: {updated_count}, New: {new_count}")
    sorted_entries = sorted(entries.values(), key=lambda x: -x['filetime'])
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(struct.pack('I', len(sorted_entries)))
        for entry in sorted_entries:
            name_bytes = entry['name'].encode('utf-16-le')
            name_len = len(name_bytes) // 2
            f.write(struct.pack('I', name_len))
            f.write(name_bytes)
            f.write(struct.pack('Q', entry['filetime']))
            f.write(struct.pack('I', len(entry['content'])))
            f.write(entry['content'])
    print(f"Written {OUTPUT_FILE} with {len(sorted_entries)} entries, {os.path.getsize(OUTPUT_FILE)} bytes")

if __name__ == '__main__':
    main()
