from PIL import Image
from sticker_maker.config import get_default_font_path
from sticker_maker.processing.typography import add_caption_to_image, load_font


def test_load_font():
    font = load_font(get_default_font_path(), size=24)
    assert font is not None


def test_add_caption():
    canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    # Test short caption
    out = add_caption_to_image(canvas, "你好", font_path=get_default_font_path())
    assert out.size == (240, 240)
    # Check that pixels were written (alpha > 0)
    alpha = out.getchannel("A")
    bbox = alpha.getbbox()
    assert bbox is not None
    # Text should be positioned at the lower half of canvas
    assert bbox[3] > 180


def test_add_long_caption():
    canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    long_text = "这是一段比较长的微信表情包中文文字"
    out = add_caption_to_image(canvas, long_text, font_path=get_default_font_path())
    assert out.size == (240, 240)
    bbox = out.getchannel("A").getbbox()
    assert bbox is not None
    # Should stay within safety margins (not bleed off x=0 or x=240)
    assert bbox[0] >= 0
    assert bbox[2] <= 240
