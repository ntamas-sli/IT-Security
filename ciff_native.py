import ctypes
import os

# CIFF
class CIFF(ctypes.Structure):
    _fields_ = [
        ("magic", ctypes.c_char * 5),
        ("header_size", ctypes.c_uint64),
        ("content_size", ctypes.c_uint64),
        ("width", ctypes.c_uint64),
        ("height", ctypes.c_uint64),
        ("caption", ctypes.c_char_p),
        ("tags", ctypes.POINTER(ctypes.c_char_p)),
        ("tag_count", ctypes.c_size_t),
        ("pixels", ctypes.POINTER(ctypes.c_ubyte)),
        ("pixel_count", ctypes.c_size_t),
        ("is_valid", ctypes.c_bool),
    ]

dll_path = os.path.abspath("ciff_parser.dll")
ciff_lib = ctypes.CDLL(dll_path)

ciff_lib.parse_ciff.argtypes = [ctypes.c_char_p]
ciff_lib.parse_ciff.restype = ctypes.POINTER(CIFF)

ciff_obj_ptr = ciff_lib.parse_ciff(b"example.ciff")
ciff = ciff_obj_ptr.contents

print("CIFF valid:", ciff.is_valid)
print("Magic:", ciff.magic.decode())
print("Size:", ciff.width, "x", ciff.height)
print("Caption:", ciff.caption.decode())

print("Tags:")
for i in range(ciff.tag_count):
    print("-", ciff.tags[i].decode())

print("Pixel count:", ciff.pixel_count)
