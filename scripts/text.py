


class TextRenderer(object)

def rasterizeString(face, string):
    slot = face.glyph

    # Loop over characters to determine bounding box
    width, height, baseline = 0, 0, 0
    for i in range(len(string)):
        prev, curr = '\0' if i is 0 else string[i-1], string[i]

        face.load_char(curr)
        bitmap = slot.bitmap

        height = max(height, bitmap.rows + max(0, -(slot.bitmap_top - bitmap.rows)))
        baseline = max(baseline, max(0, -(slot.bitmap_top - bitmap.rows)))

        kerning = face.get_kerning(prev, curr)

        width += (slot.advance.x >> 6) + (kerning.x >> 6)

    # Rasterize the string
    buffer = np.zeros((height, width), dtype=np.ubyte)
    x, y = 0, 0
    for i in range(len(string)):
        prev, curr = '\0' if i is 0 else string[i-1], string[i]

        face.load_char(curr)
        bitmap = slot.bitmap

        top = slot.bitmap_top
        left = slot.bitmap_left
        w, h = bitmap.width, bitmap.rows
        y = height - baseline - top

        kerning = face.get_kerning(prev, curr)
        x += (kerning.x >> 6)
        buffer[y:y + h, x:x + w] += np.array(bitmap.buffer, dtype='ubyte').reshape(h, w)
        x += (slot.advance.x >> 6)

    return buffer