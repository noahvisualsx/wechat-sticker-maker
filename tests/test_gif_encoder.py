from pathlib import Path
from PIL import Image, ImageSequence
from sticker_maker.processing.gif_encoder import encode_gif, synthesize_motion_frames


def test_synthesize_motion_frames():
    base = Image.new("RGBA", (240, 240), (255, 200, 200, 255))
    frames = synthesize_motion_frames(base, motion_type="laugh_bounce", frames=8)
    assert len(frames) == 8
    for f in frames:
        assert f.size == (240, 240)
        assert f.mode == "RGBA"

    # Frames should have slight motion differences
    assert frames[0].tobytes() != frames[2].tobytes()


def test_encode_gif(tmp_path: Path):
    base = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    # Make a small moving dot
    frames = []
    for i in range(8):
        f = base.copy()
        # Draw dot at different x
        for x in range(20 + i * 5, 40 + i * 5):
            for y in range(50, 70):
                f.putpixel((x, y), (255, 100, 100, 255))
        frames.append(f)

    gif_path = tmp_path / "test.gif"
    encode_gif(frames, gif_path, frame_duration_ms=180, loop=0)

    assert gif_path.exists()
    assert gif_path.stat().st_size > 0

    with Image.open(gif_path) as img:
        assert img.format == "GIF"
        assert img.size == (240, 240)
        assert img.info.get("loop") == 0
        read_frames = [f.copy() for f in ImageSequence.Iterator(img)]
        assert len(read_frames) == 8
        # Ensure motion is present
        assert read_frames[0].tobytes() != read_frames[4].tobytes()
