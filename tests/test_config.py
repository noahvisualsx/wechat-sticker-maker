import pytest
from sticker_maker.config import get_profile, PROFILES
from sticker_maker.schemas import JobConfig, sanitize_id


def test_profile_lookup():
    prof = get_profile("wechat-conservative-2026-11")
    assert prof.sticker.size == (240, 240)
    assert prof.sticker.max_bytes == 500_000
    assert prof.thumbnail.size == (120, 120)
    assert prof.thumbnail.max_bytes == 50_000
    assert prof.cover.size == (240, 240)
    assert prof.icon.size == (50, 50)
    assert prof.banner.size == (750, 400)
    assert prof.allowed_counts == [8, 16, 24]

    with pytest.raises(ValueError):
        get_profile("non_existent_profile")


def test_job_config_validation():
    job = JobConfig(
        job_id="test-job-001",
        source_image="tests/fixtures/sample_cat.png",
        output_dir="output/test-job-001",
        count=16,
    )
    assert job.job_id == "test-job-001"
    assert job.count == 16
    assert job.mode == "both"

    # Invalid count
    with pytest.raises(ValueError):
        JobConfig(
            job_id="test",
            source_image="sample.png",
            output_dir="out",
            count=10,  # only 8, 16, 24 allowed
        )


def test_sanitize_id():
    assert sanitize_id("my cat & dog #1") == "my_cat___dog__1"
    with pytest.raises(ValueError):
        sanitize_id("$$$###")
