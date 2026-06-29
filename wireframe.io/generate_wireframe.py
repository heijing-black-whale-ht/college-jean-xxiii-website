import zlib

WIDTH, HEIGHT = 1400, 900
BACKGROUND = (245, 248, 250)
ACCENT = (34, 94, 86)
TEXT = (30, 41, 51)
MUTED = (107, 114, 128)
LINE = (209, 213, 219)

# Simple pixel buffer
pixels = [BACKGROUND] * (WIDTH * HEIGHT)

# Helpers

def put_pixel(x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        pixels[y * WIDTH + x] = color


def draw_rect(x0, y0, x1, y1, color, fill=False, width=1):
    for dx in range(width):
        for x in range(x0 + dx, x1 - dx):
            put_pixel(x, y0 + dx, color)
            put_pixel(x, y1 - dx, color)
        for y in range(y0 + dx, y1 - dx):
            put_pixel(x0 + dx, y, color)
            put_pixel(x1 - dx, y, color)
    if fill:
        for y in range(y0 + width, y1 - width):
            for x in range(x0 + width, x1 - width):
                put_pixel(x, y, color)


def write_text(x, y, text, color):
    # Minimal fixed-width text boxes as wireframe labels
    label = '[' + text + ']'
    for i, ch in enumerate(label):
        ox = x + i * 8
        for dx in range(6):
            for dy in range(10):
                if 1 <= dx <= 4 and 2 <= dy <= 7:
                    put_pixel(ox + dx, y + dy, color)


def encode_png(filename):
    def png_chunk(chunk_type, data):
        chunk = chunk_type + data
        return len(data).to_bytes(4, 'big') + chunk + zlib.crc32(chunk).to_bytes(4, 'big')

    raw = b''
    for y in range(HEIGHT):
        raw += b'\x00'
        for x in range(WIDTH):
            raw += bytes(pixels[y * WIDTH + x])
    data = zlib.compress(raw, level=9)

    with open(filename, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(png_chunk(b'IHDR', WIDTH.to_bytes(4, 'big') + HEIGHT.to_bytes(4, 'big') + b'\x08\x02\x00\x00\x00') )
        f.write(png_chunk(b'IDAT', data))
        f.write(png_chunk(b'IEND', b''))


# Build layout
draw_rect(40, 40, WIDTH - 40, 110, LINE, width=2)
write_text(60, 55, 'Caribbean Coastal Retreats', ACCENT)

# Navigation
nav = ['Home', 'Destinations', 'Experiences', 'About', 'Contact']
nav_x = WIDTH - 230
for item in nav:
    write_text(nav_x, 60, item, MUTED)
    nav_x += 100

# Hero section
draw_rect(40, 150, WIDTH - 40, 510, LINE, width=2)
draw_rect(60, 170, WIDTH - 420, 490, LINE, width=2)
write_text(90, 260, 'Hero Image', MUTED)
write_text(WIDTH - 360, 190, 'Experience Luxury Caribbean Shores', TEXT)
write_text(WIDTH - 360, 230, 'High-end villas, private beaches, and bespoke escapes.', MUTED)

draw_rect(WIDTH - 360, 300, WIDTH - 160, 350, ACCENT, width=2)
write_text(WIDTH - 345, 310, 'Explore Villas', ACCENT)
draw_rect(WIDTH - 160, 300, WIDTH - 60, 350, ACCENT, width=2)
write_text(WIDTH - 145, 310, 'Plan Escape', ACCENT)

# Feature cards
card_y = 540
card_w = (WIDTH - 140) // 3
card_h = 220
for i, label in enumerate(['Private Beach Villas', 'Exclusive Yacht Tours', 'Wellness Retreats']):
    x0 = 40 + i * (card_w + 30)
    draw_rect(x0, card_y, x0 + card_w, card_y + card_h, LINE, width=2)
    draw_rect(x0 + 20, card_y + 20, x0 + card_w - 20, card_y + 110, LINE, width=2)
    write_text(x0 + 25, card_y + 40, 'Image', MUTED)
    write_text(x0 + 20, card_y + 130, label, TEXT)
    write_text(x0 + 20, card_y + 160, 'Premium travel experience', MUTED)

# Footer
draw_rect(40, 780, WIDTH - 40, 880, LINE, width=2)
cols = ['About', 'Destinations', 'Services', 'Contact']
for i, heading in enumerate(cols):
    x0 = 50 + i * 320
    write_text(x0, 795, heading, ACCENT)
    write_text(x0, 825, 'Link 1', MUTED)
    write_text(x0, 855, 'Link 2', MUTED)
    write_text(x0, 885, 'Link 3', MUTED)

# Save PNG
encode_png('wireframe.png')
print('Created wireframe.io/wireframe.png')
