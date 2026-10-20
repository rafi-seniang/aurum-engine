import struct
import zlib
import os

def create_png(width, height, rgb_color, output_path):
    # PNG signature
    png = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
    png += struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    # IDAT chunk (raw scanlines)
    # rgb_color = (R, G, B)
    r, g, b = rgb_color
    line = b'\x00' + bytes([r, g, b]) * width
    raw_data = line * height
    compressed = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed)
    png += struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    # IEND chunk
    iend_crc = zlib.crc32(b'IEND')
    png += struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(png)
    print(f"Generated PNG icon at {output_path} ({width}x{height})")

if __name__ == '__main__':
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    # Gold color #F59E0B -> (245, 158, 11)
    create_png(192, 192, (245, 158, 11), os.path.join(base_dir, 'public', 'icon-192.png'))
    create_png(512, 512, (245, 158, 11), os.path.join(base_dir, 'public', 'icon-512.png'))
    create_png(192, 192, (245, 158, 11), os.path.join(base_dir, 'dist', 'icon-192.png'))
    create_png(512, 512, (245, 158, 11), os.path.join(base_dir, 'dist', 'icon-512.png'))
