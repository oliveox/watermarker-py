import pytest

from src.config import config_manager
from src.media_processing import get_video_orientation
from src.utils import watermark_image, watermark_video


@pytest.mark.parametrize(
    "file_path,expected_orientation",
    [
        # ("tests/resources/waves.mp4", "landscape"),
        # ("tests/resources/waves.mp4", "landscape"),
        ("tests/resources/underwater.MP4", "landscape"),
    ],
)
def test_get_orientation_metadata(file_path, expected_orientation):
    # TODO - video with rotate data
    actual_orientation = get_video_orientation(file_path)
    assert actual_orientation == expected_orientation


# @pytest.mark.parametrize(
#     "file_path,expected_orientation",
#     [
#         #     ("tests/resources/sky.JPG", "landscape"),
#         # ("tests/resources/crane.JPG", "portrait"),
#     ],
# )
# def test_get_orientation_metadata(file_path, expected_orientation):
#     # TODO - video with rotate data
#     actual_orientation = get_image_orientation(file_path)
#     assert actual_orientation == expected_orientation


@pytest.mark.parametrize(
    "file_path,expected_orientation",
    [
        ("tests/resources/sky.JPG", "landscape"),
        # ("tests/resources/crane.JPG", "portrait"),
    ],
)
def test_watermark_image(file_path, expected_orientation):
    config_manager.set_watermark_file_path("tests/resources/watermark.png")
    config_manager.set_output_dir_path("tests/resources/output/watermarked.jpg")
    watermark_image(file_path)


@pytest.mark.parametrize(
    "file_path,expected_orientation",
    [
        ("tests/resources/plane.MP4", "landscape"),
    ],
)
def test_watermark_video(file_path, expected_orientation):
    config_manager.set_watermark_file_path("tests/resources/watermark.png")
    config_manager.set_output_dir_path("tests/resources/output/watermarked.mp4")
    watermark_video(file_path)


# def test_load_configuration_file():
#     from src.config import config_manager
#
#     watermark_config = config_manager.config["WATERMARK"]
