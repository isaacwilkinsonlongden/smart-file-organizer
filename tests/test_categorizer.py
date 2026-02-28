from pathlib import Path
from organizer.categorizer import get_category


def test_jpg_is_images():
    assert get_category(Path("photo.jpg")) == "Images"


def test_uppercase_extension():
    assert get_category(Path("PHOTO.JPG")) == "Images"


def test_no_extension():
    assert get_category(Path("README")) == "Other"


def test_archive_tar_gz():
    assert get_category(Path("archive.tar.gz")) == "Archives"