import pytest
import logging
from src.ciff import CIFF
from os import walk


LOGGER = logging.getLogger(__name__)

valid_images = next(walk("test-images/"), (None, None, []))[2]
invalid_images = [
    {
        "path": "test-images-invalid/invalid1.ciff",
        "error": "Invalid magic: lowercase magic character"
    },
    {
        "path": "test-images-invalid/invalid2.ciff",
        "error": "Invalid magic: last character of magic missing"
    },
    {
        "path": "test-images-invalid/invalid3.ciff",
        "error": "Invalid header size: header size is 0"
    },
    {
        "path": "test-images-invalid/invalid4.ciff",
        "error": "Invalid content size: content size is ULONG_MAX, no pixels"
    },
    {
        "path": "test-images-invalid/invalid5.ciff",
        "error": "Invalid height: height is ULONG_MAX"
    }
]


@pytest.mark.parametrize("filename", valid_images)
def test_valid_ciff_files(filename):
    LOGGER.info(f"Running test on: test-images/{filename}")
    ciff = CIFF().parse_ciff_file(f"test-images/{filename}")
    LOGGER.info(f"Ciff validity: {ciff.is_valid}")
    assert ciff.is_valid == True


@pytest.mark.parametrize("task", invalid_images)
def test_invalid_ciff_files(task):
    LOGGER.info(f"Running test on: {task['path']}")
    LOGGER.debug(f"Expected problem: {task['error']}")
    ciff = CIFF().parse_ciff_file(task['path'])
    LOGGER.info(f"Ciff validity: {ciff.is_valid}")
    assert ciff.is_valid == False
