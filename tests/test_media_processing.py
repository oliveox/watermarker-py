# import pytest
#
# from src.config import config_manager
# from src.utils import watermark_image, watermark_video
#
#
# @pytest.mark.parametrize(
#     "file_path,expected_orientation",
#     [
#         ("tests/resources/sky.JPG", "landscape"),
#         # ("tests/resources/crane.JPG", "portrait"),
#     ],
# )
# def test_watermark_image(file_path, expected_orientation):
#     config_manager.set_watermark_file_path("tests/resources/watermark.png")
#     config_manager.set_output_dir_path("tests/resources/output/watermarked.jpg")
#     watermark_image(file_path)
#
#
# @pytest.mark.parametrize(
#     "file_path,expected_orientation",
#     [
#         ("tests/resources/plane.MP4", "landscape"),
#     ],
# )
# def test_watermark_video(file_path, expected_orientation):
#     config_manager.set_watermark_file_path("tests/resources/watermark.png")
#     config_manager.set_output_dir_path("tests/resources/output/watermarked.mp4")
#     watermark_video(file_path)
