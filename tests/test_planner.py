import pytest
from sticker_maker.planner import load_all_presets, plan_expressions


def test_presets_uniqueness_and_validity():
    presets = load_all_presets()
    assert len(presets) >= 24

    ids = [p.id for p in presets]
    captions = [p.caption for p in presets]

    assert len(ids) == len(set(ids)), "Preset IDs must be unique"
    assert len(captions) == len(set(captions)), "Captions must be unique"
    for p in presets:
        assert p.id.strip() != ""
        assert p.caption.strip() != ""
        assert p.mood.strip() != ""
        assert p.static_pose.strip() != ""
        assert p.motion.frames >= 2


def test_plan_expressions_counts():
    plan8 = plan_expressions(count=8)
    assert len(plan8) == 8
    # 8-pack should contain essential friendly actions
    captions8 = {p.caption for p in plan8}
    assert "你好" in captions8
    assert "晚安" in captions8
    assert "谢谢" in captions8

    plan16 = plan_expressions(count=16)
    assert len(plan16) == 16

    plan24 = plan_expressions(count=24)
    assert len(plan24) == 24

    with pytest.raises(ValueError):
        plan_expressions(count=12)
