"""Processing tools for transparency, typography, resizing, and GIF encoding."""

from .alpha import apply_safe_margin, ensure_alpha_channel, remove_matte_background
from .gif_encoder import encode_gif, synthesize_motion_frames
from .optimizer import optimize_gif, optimize_png
from .resize import create_banner, create_icon, create_thumbnail, resize_sticker
from .typography import add_caption_to_image, load_font

__all__ = [
    "apply_safe_margin",
    "ensure_alpha_channel",
    "remove_matte_background",
    "encode_gif",
    "synthesize_motion_frames",
    "optimize_gif",
    "optimize_png",
    "create_banner",
    "create_icon",
    "create_thumbnail",
    "resize_sticker",
    "add_caption_to_image",
    "load_font",
]
