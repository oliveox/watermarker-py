from functools import cache
from typing import Optional


class FFmpegUtilsMixin:
    @staticmethod
    def get_watermarking_command(
        input_file_path: str,
        watermark_path: str,
        output_file_path: str,
        transpose: str,
        overlay: str,
        watermark_scaling: str,
    ) -> str:
        return (
            f"ffmpeg -y -i {input_file_path} -i {watermark_path} "
            f'-filter_complex "{transpose}{watermark_scaling}{overlay}" "{output_file_path}"'
        )

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
            print(f"Invalid watermark position: {position}")

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

        if position == "NE":
            overlay = (
                f"0{get_horizontal_margins(margin_east, margin_west)}"
                f":0{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "NC":
            overlay = (
                f"(main_w/2-overlay_w/2{get_horizontal_margins(margin_east, margin_west)}"
                f":0{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "NW":
            overlay = (
                f"main_w-overlay_w{get_horizontal_margins(margin_east, margin_west)}"
                f":0{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "SE":
            overlay = (
                f"0{get_horizontal_margins(margin_east, margin_west)}"
                f":main_h-overlay_h{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "SC":
            overlay = (
                f"(main_w/2-overlay_w/2{get_horizontal_margins(margin_east, margin_west)}"
                f":main_h-overlay_h{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "SW":
            overlay = (
                f"main_w-overlay_w{get_horizontal_margins(margin_east, margin_west)}"
                f":main_h-overlay_h{get_vertical_margins(margin_nord, margin_south)}"
            )
        elif position == "C":
            overlay = (
                f"(main_w/2-overlay_w/2{get_horizontal_margins(margin_east, margin_west)}"
                f":(main_h/2-overlay_h/2{get_vertical_margins(margin_nord, margin_south)})"
            )
        elif position == "CE":
            overlay = (
                f"0{get_horizontal_margins(margin_east, margin_west)}"
                f":(main_h/2-overlay_h/2{get_vertical_margins(margin_nord, margin_south)})"
            )
        elif position == "CW":
            overlay = (
                f"main_w-overlay_w{get_horizontal_margins(margin_east, margin_west)}"
                f":(main_h/2-overlay_h/2{get_vertical_margins(margin_nord, margin_south)})"
            )
        else:
            print(f"Invalid watermark position: {position}")

        return f"overlay={overlay}"
