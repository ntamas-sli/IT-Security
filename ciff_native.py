import ctypes
from ctypes import c_char_p, c_int64, c_uint8, POINTER, Structure
import os


class Pixel(Structure):
    _fields_ = [("r", c_uint8), ("g", c_uint8), ("b", c_uint8)]


class CIFF(Structure):
    _fields_ = [
        ("is_valid", ctypes.c_bool),
        ("magic", c_char_p),
        ("header_size", c_int64),
        ("content_size", c_int64),
        ("width", c_int64),
        ("height", c_int64),
        ("caption", c_char_p),
        ("tags", c_char_p),
        ("pixels", Pixel),
    ]


lib = ctypes.CDLL("./ciff.dll")

def load_native_ciff_image(file_path: str) -> CIFF:
    img_ptr = lib.parse_ciff_file(file_path.encode("utf-8"))
    if not img_ptr:
        raise RuntimeError("Parser returned null pointer")
    return img_ptr.contents
