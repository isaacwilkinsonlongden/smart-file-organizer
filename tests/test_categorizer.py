from pathlib import Path

from organizer.categorizer import EXT_TO_CATEGORY, get_category


def test_jpg_is_images():
    assert get_category(
        Path("photo.jpg"),
        EXT_TO_CATEGORY,
        "Other",
        True,
    ) == "Images"


def test_uppercase_extension():
    assert get_category(
        Path("PHOTO.JPG"),
        EXT_TO_CATEGORY,
        "Other",
        True,
    ) == "Images"


def test_no_extension_uses_fallback_when_enabled():
    assert get_category(
        Path("README"),
        EXT_TO_CATEGORY,
        "Other",
        True,
    ) == "Other"


def test_no_extension_is_skipped_when_fallback_disabled():
    assert get_category(
        Path("README"),
        EXT_TO_CATEGORY,
        "Other",
        False,
    ) is None


def test_archive_tar_gz():
    assert get_category(
        Path("archive.tar.gz"),
        EXT_TO_CATEGORY,
        "Other",
        True,
    ) == "Archives"


def test_unknown_extension_uses_fallback_when_enabled():
    assert get_category(
        Path("file.unknown"),
        EXT_TO_CATEGORY,
        "Other",
        True,
    ) == "Other"


def test_unknown_extension_is_skipped_when_fallback_disabled():
    assert get_category(
        Path("file.unknown"),
        EXT_TO_CATEGORY,
        "Other",
        False,
    ) is None


def test_custom_mapping_overrides_default_behavior():
    custom_map = EXT_TO_CATEGORY.copy()
    custom_map[".mp3"] = "Music"

    assert get_category(
        Path("song.mp3"),
        custom_map,
        "Other",
        True,
    ) == "Music"