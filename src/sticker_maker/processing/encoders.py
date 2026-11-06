"""Platform-format encoders with size budgets: PNG, JPG, WebP (static/animated), GIF, APNG,
WEBM (VP9 + alpha, Telegram video stickers) and MP4 (H.264 showcase videos) via ffmpeg."""

from __future__ import annotations

import io
import logging
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from PIL import Image

from ..styles import hex_to_rgba
from .gif_encoder import encode_gif

logger = logging.getLogger(__name__)


class ExportUnavailable(RuntimeError):
    """Raised when an encoder dependency (e.g. ffmpeg) is missing."""


def ffmpeg_bin() -> Optional[str]:
    return shutil.which("ffmpeg")


def ffprobe_bin() -> Optional[str]:
    return shutil.which("ffprobe")


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------


def fit_to_canvas(
    img: Image.Image,
    out_size: Tuple[int, int],
    margin_px: int = 0,
    transparent: bool = True,
    background: Optional[str] = None,
) -> Image.Image:
    """Scale the (square master) sticker into an output canvas with a transparent safe margin."""
    ow, oh = out_size
    src = img.convert("RGBA")
    box_w, box_h = max(1, ow - 2 * margin_px), max(1, oh - 2 * margin_px)
    scale = min(box_w / float(src.width), box_h / float(src.height))
    nw, nh = max(1, int(round(src.width * scale))), max(1, int(round(src.height * scale)))
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS) if (nw, nh) != src.size else src
    bg = (0, 0, 0, 0) if transparent else hex_to_rgba(background or "#FFFFFF")
    canvas = Image.new("RGBA", (ow, oh), bg)
    canvas.alpha_composite(resized, ((ow - nw) // 2, (oh - nh) // 2))
    return canvas


def _atomic_write(path: Path, data: bytes) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return len(data)


# ---------------------------------------------------------------------------
# Static encoders
# ---------------------------------------------------------------------------


def encode_png_bytes(img: Image.Image, max_bytes: int) -> bytes:
    rgba = img.convert("RGBA")
    buf = io.BytesIO()
    rgba.save(buf, format="PNG", optimize=True)
    if buf.tell() <= max_bytes:
        return buf.getvalue()
    for colors in (256, 128, 64, 32):
        buf = io.BytesIO()
        rgba.quantize(colors=colors, method=Image.Quantize.FASTOCTREE).save(buf, format="PNG", optimize=True)
        if buf.tell() <= max_bytes:
            return buf.getvalue()
    return buf.getvalue()


def encode_webp_bytes(img: Image.Image, max_bytes: int) -> bytes:
    rgba = img.convert("RGBA")
    buf = io.BytesIO()
    rgba.save(buf, format="WEBP", lossless=True, method=4, exact=False)
    if buf.tell() <= max_bytes:
        return buf.getvalue()
    for q in (92, 85, 78, 70, 60, 50, 40, 30, 20):
        buf = io.BytesIO()
        rgba.save(buf, format="WEBP", quality=q, method=6, alpha_quality=max(60, q))
        if buf.tell() <= max_bytes:
            return buf.getvalue()
    return buf.getvalue()


def encode_jpg_bytes(img: Image.Image, max_bytes: int, background: str = "#FFFFFF") -> bytes:
    rgba = img.convert("RGBA")
    bg = Image.new("RGBA", rgba.size, hex_to_rgba(background))
    rgb = Image.alpha_composite(bg, rgba).convert("RGB")
    data = b""
    for q in (92, 86, 80, 72, 64, 55):
        buf = io.BytesIO()
        rgb.save(buf, format="JPEG", quality=q, optimize=True, progressive=True)
        data = buf.getvalue()
        if len(data) <= max_bytes:
            break
    return data


def save_static(img: Image.Image, path: Path, fmt: str, max_bytes: int, background: Optional[str] = None) -> int:
    if fmt == "png":
        data = encode_png_bytes(img, max_bytes)
    elif fmt == "webp":
        data = encode_webp_bytes(img, max_bytes)
    elif fmt == "jpg":
        data = encode_jpg_bytes(img, max_bytes, background or "#FFFFFF")
    else:
        raise ValueError(f"Unsupported static format: {fmt}")
    return _atomic_write(path, data)


# ---------------------------------------------------------------------------
# Animation timing helpers
# ---------------------------------------------------------------------------


def plan_timing(
    n_frames: int,
    frame_ms: int,
    max_duration_ms: Optional[int] = None,
    max_fps: Optional[int] = None,
    min_frame_ms: Optional[int] = None,
) -> int:
    dur = max(20, int(frame_ms))
    if max_duration_ms and n_frames * dur > max_duration_ms:
        dur = max(1, max_duration_ms // max(1, n_frames))
    if max_fps:
        dur = max(dur, int(math.ceil(1000.0 / max_fps)))
    if min_frame_ms:
        dur = max(dur, min_frame_ms)
    return dur


def adjust_frame_count(frames: Sequence[Image.Image], min_frames: Optional[int], max_frames: Optional[int]) -> List[Image.Image]:
    out = list(frames)
    if max_frames and len(out) > max_frames:
        step = len(out) / float(max_frames)
        out = [out[int(i * step)] for i in range(max_frames)]
    if min_frames and len(out) < min_frames:
        reps = int(math.ceil(min_frames / float(len(out))))
        out = [f for f in out for _ in range(reps)][: max(min_frames, len(out))]
    return out


def _subsample(frames: List[Image.Image], dur: int) -> Tuple[List[Image.Image], int]:
    if len(frames) <= 2:
        return frames, dur
    return frames[::2], dur * 2


# ---------------------------------------------------------------------------
# Animated encoders
# ---------------------------------------------------------------------------


def save_gif(frames: List[Image.Image], path: Path, dur: int, loop: int, max_bytes: int) -> int:
    work = list(frames)
    for _attempt in range(3):
        for colors in (254, 160, 96, 64, 32):
            encode_gif(work, path, frame_duration_ms=dur, loop=loop, max_colors=colors)
            size = path.stat().st_size
            if size <= max_bytes:
                return size
        if len(work) <= 4:
            break
        work, dur = _subsample(work, dur)
    return path.stat().st_size


def save_animated_webp(frames: List[Image.Image], path: Path, dur: int, loop: int, max_bytes: int) -> int:
    work = [f.convert("RGBA") for f in frames]
    data = b""
    for _attempt in range(3):
        for q in (85, 75, 65, 55, 45, 35, 25):
            buf = io.BytesIO()
            work[0].save(
                buf,
                format="WEBP",
                save_all=True,
                append_images=work[1:],
                duration=dur,
                loop=loop,
                quality=q,
                method=4,
                alpha_quality=max(50, q),
                minimize_size=True,
            )
            data = buf.getvalue()
            if len(data) <= max_bytes:
                return _atomic_write(path, data)
        if len(work) <= 4:
            break
        work, dur = _subsample(work, dur)
    return _atomic_write(path, data)


def save_apng(frames: List[Image.Image], path: Path, dur: int, loop: int, max_bytes: int, min_frames: Optional[int] = None) -> int:
    work = [f.convert("RGBA") for f in frames]
    data = b""
    for _attempt in range(3):
        for colors in (None, 256, 128, 64, 32):
            seq = work if colors is None else [f.quantize(colors=colors, method=Image.Quantize.FASTOCTREE) for f in work]
            buf = io.BytesIO()
            seq[0].save(
                buf,
                format="PNG",
                save_all=True,
                append_images=seq[1:],
                duration=dur,
                loop=loop,
                disposal=0,
                blend=0,
                compress_level=6,
            )
            data = buf.getvalue()
            if len(data) <= max_bytes:
                return _atomic_write(path, data)
        if len(work) <= max(4, min_frames or 0):
            break
        work, dur = _subsample(work, dur)
    return _atomic_write(path, data)


def _write_frame_sequence(frames: Sequence[Image.Image], tmpdir: Path, rgb_background: Optional[str] = None) -> str:
    for i, f in enumerate(frames):
        img = f.convert("RGBA")
        if rgb_background:
            bg = Image.new("RGBA", img.size, hex_to_rgba(rgb_background))
            img = Image.alpha_composite(bg, img).convert("RGB")
        img.save(tmpdir / f"f_{i:04d}.png", format="PNG", compress_level=1)
    return str(tmpdir / "f_%04d.png")


def save_webm(frames: List[Image.Image], path: Path, dur: int, max_bytes: int, max_duration_ms: Optional[int] = None) -> int:
    """VP9 + alpha WEBM (Telegram video sticker style). Requires ffmpeg with libvpx-vp9."""
    ff = ffmpeg_bin()
    if not ff:
        raise ExportUnavailable("ffmpeg not found: install ffmpeg (brew install ffmpeg) to export WEBM video stickers")
    fps = 1000.0 / max(1, dur)
    total_s = len(frames) * dur / 1000.0
    if max_duration_ms:
        total_s = min(total_s, max_duration_ms / 1000.0 - 0.01)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        pattern = _write_frame_sequence(frames, Path(td))
        tmp_out = Path(td) / "out.webm"
        for crf in (30, 36, 42, 48, 54, 60, 63):
            cmd = [
                ff, "-y", "-loglevel", "error", "-framerate", f"{fps:.4f}", "-i", pattern,
                "-t", f"{total_s:.3f}", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
                "-b:v", "0", "-crf", str(crf), "-deadline", "good", "-row-mt", "1", "-an", str(tmp_out),
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            if tmp_out.stat().st_size <= max_bytes:
                break
        return _atomic_write(path, tmp_out.read_bytes())


def save_mp4(frames: List[Image.Image], path: Path, dur: int, seconds: float = 6.0, background: str = "#FFFFFF") -> int:
    """H.264 MP4 (yuv420p, faststart) looping the frame cycle to ~``seconds`` for Reels/TikTok/Douyin."""
    ff = ffmpeg_bin()
    if not ff:
        raise ExportUnavailable("ffmpeg not found: install ffmpeg (brew install ffmpeg) to export MP4 showcase videos")
    fps = 1000.0 / max(1, dur)
    cycle_s = len(frames) * dur / 1000.0
    loops = max(0, int(math.ceil(seconds / max(0.05, cycle_s))) - 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        pattern = _write_frame_sequence(frames, Path(td), rgb_background=background)
        tmp_out = Path(td) / "out.mp4"
        cmd = [
            ff, "-y", "-loglevel", "error", "-stream_loop", str(loops), "-framerate", f"{fps:.4f}", "-i", pattern,
            "-t", f"{seconds:.3f}", "-vf", "fps=30,scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "veryfast",
            "-movflags", "+faststart", "-an", str(tmp_out),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return _atomic_write(path, tmp_out.read_bytes())


def save_animated(
    frames: List[Image.Image],
    path: Path,
    fmt: str,
    frame_ms: int,
    max_bytes: int,
    loop: int = 0,
    max_duration_ms: Optional[int] = None,
    max_fps: Optional[int] = None,
    min_frame_ms: Optional[int] = None,
    min_frames: Optional[int] = None,
    max_frames: Optional[int] = None,
) -> int:
    frames = adjust_frame_count(frames, min_frames, max_frames)
    dur = plan_timing(len(frames), frame_ms, max_duration_ms, max_fps, min_frame_ms)
    if fmt == "gif":
        return save_gif(frames, path, dur, loop, max_bytes)
    if fmt == "webp":
        return save_animated_webp(frames, path, dur, loop, max_bytes)
    if fmt == "apng":
        if loop and max_duration_ms:
            cycle = len(frames) * dur
            loop = max(1, min(loop, max_duration_ms // max(1, cycle)))
        return save_apng(frames, path, dur, loop, max_bytes, min_frames)
    if fmt == "webm":
        return save_webm(frames, path, dur, max_bytes, max_duration_ms)
    if fmt == "mp4":
        return save_mp4(frames, path, dur)
    raise ValueError(f"Unsupported animated format: {fmt}")


def probe_video(path: Path) -> Optional[dict]:
    fp = ffprobe_bin()
    if not fp:
        return None
    try:
        import json

        res = subprocess.run(
            [fp, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,codec_name,pix_fmt",
             "-show_entries", "format=duration", "-of", "json", str(path)],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(res.stdout)
        stream = (data.get("streams") or [{}])[0]
        return {
            "width": stream.get("width"),
            "height": stream.get("height"),
            "codec": stream.get("codec_name"),
            "pix_fmt": stream.get("pix_fmt"),
            "duration": float(data.get("format", {}).get("duration", 0) or 0),
            "has_audio": False,
        }
    except Exception as e:  # pragma: no cover - environment dependent
        logger.warning("ffprobe failed for %s: %s", path, e)
        return None
