import struct
import micropython
import sys
import os

sys.path.insert(0, "/system/apps/bad_apple")
os.chdir("/system/apps/bad_apple")


from badgeware import run


framerate = 15
brightness = 255
video = open("badapple39x26.bin", "rb")


# This Micropython Viper function is compiled to native code
# for maximum execution speed.
@micropython.viper
def render(target: ptr32, source: ptr8, length: int):  # noqa: F821
    offset = 0
    for i in range(0, length, 2):
        # The encoded video data is an array of span lengths and greyscale colour values
        span_len = source[i]

        # The encoder discards two bits of colour information to optimise run lengths
        # throw one empty bit away to reduce max overall brightness
        colour = source[i + 1] >> 1

        # Expand the grey colour to each colour channel and populate alpha
        c = (int(255) << 24) | (colour << 16) | (colour << 8) | colour

        # "Draw" the span
        for span_offset in range(span_len):
            target[offset + span_offset] = c

        offset += span_len


# offscreen canvas for drawing our video
canvas = image(39, 26)
target = memoryview(canvas)

# worst case frame is a run for every pixel
source = bytearray(screen.width * screen.height * 2)

pos = vec2(0, 0)
delay_until = 0
frame_count = 0


def update():
    global delay_until

    t_start = badge.ticks

    # Always blit the canvas, or we'll get flicker
    canvas.alpha = brightness
    screen.blit(canvas, canvas.clip, screen.clip)

    if delay_until > t_start:
        return

    next_frame = video.read(2)
    if len(next_frame) < 2:
        video.seek(0)
        delay_until = t_start + 4000
        canvas.pen = color.rgb(0, 0, 0)
        canvas.clear()
        return

    frame_length = struct.unpack("<H", next_frame)[0]
    _ = video.readinto(source, frame_length)
    render(target, source, frame_length)

    # Add some frame pacing, or we'll eat this video for lunch
    delay_until = t_start + 1000 / framerate


if __name__ == "__main__":
    run(update)
