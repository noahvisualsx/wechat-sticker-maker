from pathlib import Path
from PIL import Image, ImageDraw, ImageSequence
from sticker_maker.processing.gif_encoder import (
    align_ai_keyframes,
    assemble_gif_from_keyframe_files,
    assemble_gif_from_sprite_sheet,
    encode_gif,
    postprocess_raw_gif,
    slice_and_align_sprite_sheet,
    synthesize_motion_frames,
)
from sticker_maker.processing.optimizer import optimize_gif


def _make_ai_keyframe_pose(hand_offset_x: int = 0, eyes_closed: bool = False) -> Image.Image:
    """Simulate an AI-generated character keyframe with distinct hand wave position and eye state."""
    img = Image.new("RGBA", (256, 256), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Stationary lower torso (centered at x=128)
    draw.rounded_rectangle([84, 145, 172, 225], radius=16, fill=(55, 65, 90, 255))
    # Head
    draw.ellipse([84, 55, 172, 148], fill=(250, 224, 210, 255), outline=(90, 70, 65, 255), width=3)
    # Eyes (AI-drawn open vs closed blink arc)
    if eyes_closed:
        draw.arc([100, 96, 118, 108], start=190, end=350, fill=(40, 32, 32, 255), width=3)
        draw.arc([138, 96, 156, 108], start=190, end=350, fill=(40, 32, 32, 255), width=3)
    else:
        draw.ellipse([102, 94, 116, 108], fill=(35, 30, 30, 255))
        draw.ellipse([140, 94, 154, 108], fill=(35, 30, 30, 255))
    # Raised right hand at distinct AI-drawn wave position
    hx = 182 + hand_offset_x
    draw.rounded_rectangle([hx, 78, hx + 32, 136], radius=10, fill=(250, 224, 210, 255), outline=(90, 70, 65, 255), width=2)
    return img


def test_align_ai_keyframes_anchors_torso_despite_hand_wave():
    kf0 = _make_ai_keyframe_pose(hand_offset_x=0, eyes_closed=False)
    kf1 = _make_ai_keyframe_pose(hand_offset_x=14, eyes_closed=True)
    kf2 = _make_ai_keyframe_pose(hand_offset_x=28, eyes_closed=False)
    kf3 = _make_ai_keyframe_pose(hand_offset_x=10, eyes_closed=False)

    frames = align_ai_keyframes([kf0, kf1, kf2, kf3], target_size=(240, 240), die_cut_border_px=4, target_frames=8)
    assert len(frames) == 8
    for f in frames:
        assert f.size == (240, 240)
        assert f.mode == "RGBA"

    # Frame 0 (open eyes, hand left) and Frame 1 (closed eyes, hand mid) must differ in eye and hand regions
    assert frames[0].tobytes() != frames[1].tobytes()
    assert frames[1].tobytes() != frames[2].tobytes()


def test_slice_and_align_sprite_sheet_and_one_step_assemblers(tmp_path: Path):
    sheet = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
    poses = [
        (0, 0, 0, False),
        (256, 0, 12, True),
        (0, 256, 24, False),
        (256, 256, 8, True),
    ]
    kf_files = []
    for idx, (ox, oy, h_off, closed) in enumerate(poses):
        quad = _make_ai_keyframe_pose(hand_offset_x=h_off, eyes_closed=closed)
        sheet.paste(quad, (ox, oy))
        kf_path = tmp_path / f"kf_{idx}.png"
        quad.save(kf_path)
        kf_files.append(kf_path)

    sheet_path = tmp_path / "ai_2x2_sheet.png"
    sheet.save(sheet_path)

    gif_from_sheet = tmp_path / "from_sheet.gif"
    static_from_sheet = tmp_path / "from_sheet_static.png"
    assemble_gif_from_sprite_sheet(
        sheet_path=sheet_path,
        gif_output_path=gif_from_sheet,
        static_output_path=static_from_sheet,
        caption="你好",
        style="real-cutout",
        target_frames=8,
    )
    assert gif_from_sheet.exists()
    assert static_from_sheet.exists()
    with Image.open(gif_from_sheet) as gimg:
        assert gimg.size == (240, 240)
        assert gimg.n_frames == 8
        assert gimg.info.get("transparency") == 0

    gif_from_kfs = tmp_path / "from_kfs.gif"
    assemble_gif_from_keyframe_files(
        frame_paths=kf_files,
        gif_output_path=gif_from_kfs,
        caption="你好",
        style="real-cutout",
        target_frames=8,
    )
    assert gif_from_kfs.exists()


def test_synthesize_motion_frames():
    base = _make_ai_keyframe_pose(hand_offset_x=0, eyes_closed=False).resize((240, 240))
    for motion in (
        "wave_hand",
        "laugh_bounce",
        "blink_and_blush",
        "teardrop_fall",
        "stomp_and_steam",
        "head_tilt",
        "shock_shake",
        "zzz_float",
    ):
        frames = synthesize_motion_frames(base, motion_type=motion, frames=8)
        assert len(frames) == 8
        for f in frames:
            assert f.size == (240, 240)
            assert f.mode == "RGBA"
        assert frames[0].tobytes() != frames[2].tobytes()


def test_encode_gif(tmp_path: Path):
    base = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    frames = []
    for i in range(8):
        f = base.copy()
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
        assert img.info.get("transparency") == 0
        read_frames = [f.copy() for f in ImageSequence.Iterator(img)]
        assert len(read_frames) == 8
        assert read_frames[0].tobytes() != read_frames[4].tobytes()


def test_postprocess_raw_gif_and_optimize_preserves_transparency(tmp_path: Path):
    raw_frames = []
    for i in range(4):
        f = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        for x in range(180 + i * 10, 320 + i * 10):
            for y in range(180, 320):
                f.putpixel((x, y), (240, 150 + i * 15, 160, 255))
        raw_frames.append(f)

    raw_gif = tmp_path / "raw_512.gif"
    encode_gif(raw_frames, raw_gif, frame_duration_ms=180, loop=0)

    processed_gif = tmp_path / "processed_240.gif"
    postprocess_raw_gif(raw_gif, processed_gif, caption="害羞", target_size=(240, 240))

    optimize_gif(processed_gif, max_bytes=100)

    with Image.open(processed_gif) as img:
        assert img.size == (240, 240)
        assert img.info.get("transparency") == 0
