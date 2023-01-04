from functools import cache
from typing import Optional

from logger import logger


class FFmpegUtilsMixin:
    @staticmethod
    def get_watermarking_command(
        input_file_path: str,
        watermark_path: str,
        output_file_path: str,
        overlay: str,
        watermark_scaling: str,
    ) -> list[str]:
        return [
            "ffmpeg",
            "-i",
            input_file_path,
            "-i",
            watermark_path,
            "-filter_complex",
            f"{watermark_scaling}{overlay}",
            output_file_path,
        ]

    @staticmethod
    @cache
    def get_overlay(
        position: str,
        margin_nord: Optional[int],
        margin_south: Optional[int],
        margin_east: Optional[int],
        margin_west: Optional[int],
    ) -> str:
        overlay = ""
        if position not in ["NE", "NC", "NW", "SE", "SC", "SW", "C", "CE", "CW"]:
            logger.debug(f"Invalid watermark position: {position}")

        if not margin_nord:
            margin_nord = 0
        if not margin_south:
            margin_south = 0
        if not margin_east:
            margin_east = 0
        if not margin_west:
            margin_west = 0

        def get_sign(value: int, inverse: bool) -> str:
            if value > 0:
                sign = "-" if inverse else "+"
            else:
                sign = "+" if inverse else "-"

            return f"{sign}{abs(value)}"

        def get_horizontal_margins(east: int, west: int) -> str:
            return f"{get_sign(east, False)}{get_sign(west, True)}"

        def get_vertical_margins(nord: int, south: int) -> str:
            return f"{get_sign(nord, False)}{get_sign(south, True)}"

        # TODO - transform in a dict e.g.{"NE":(etc.)}
        # W / H - main input width and height
        # w / h - watermark width and height
        if position == "NE":
            overlay = (
                f"0{get_horizontal_margins(margin_east, margin_west)}"
                f":0{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "NC":
            overlay = (
                f"(W/2-w/2{get_horizontal_margins(margin_east, margin_west)}"
                f":0{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "NW":
            overlay = (
                f"W-w{get_horizontal_margins(margin_east, margin_west)}"
                f":0{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "SE":
            overlay = (
                f"0{get_horizontal_margins(margin_east, margin_west)}"
                f":H-h{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "SC":
            overlay = (
                f"(W/2-w/2{get_horizontal_margins(margin_east, margin_west)}"
                f":H-h{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "SW":
            overlay = (
                f"W-w{get_horizontal_margins(margin_east, margin_west)}"
                f":H-h{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "C":
            overlay = (
                f"(W/2-w/2{get_horizontal_margins(margin_east, margin_west)}"
                f":(H/2-h/2{get_vertical_margins(margin_nord, margin_south)})"
            )
        elif position == "CE":
            overlay = (
                f"0{get_horizontal_margins(margin_east, margin_west)}"
                f":(H/2-h/2{get_vertical_margins(margin_nord, margin_south)})"
            )
        elif position == "CW":
            overlay = (
                f"W-w{get_horizontal_margins(margin_east, margin_west)}"
                f":(H/2-h/2{get_vertical_margins(margin_nord, margin_south)})"
            )
        else:
            logger.debug(f"Invalid watermark position: {position}")

        return f"overlay={overlay}"
