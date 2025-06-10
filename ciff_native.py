import ctypes
from ctypes import c_char_p, Structure, POINTER, c_int64, c_bool, c_uint8
from ciff import CIFF

# Definiáljuk a struct-okat Pythonban is
class RGBPixel(ctypes.Structure):
    _fields_ = [("r", c_uint8),
                ("g", c_uint8),
                ("b", c_uint8)]

class CIFF_Export(Structure):
    _fields_ = [
        ("magic", ctypes.c_char_p),
        ("header_size", c_int64),
        ("content_size", c_int64),
        ("width", c_int64),
        ("height", c_int64),
        ("caption", ctypes.c_char_p),
        ("tags", POINTER(c_char_p)),
        ("pixels", POINTER(RGBPixel)),
        ("is_valid", c_bool)
    ]

def load_native_ciff_image(filepath):
    lib = ctypes.cdll.LoadLibrary(filepath)

    lib.parse.argtypes = [c_char_p]
    lib.parse.restype = POINTER(CIFF_Export)

    filepath = b"./test-vectors/test1.ciff"
    ciff_ptr = lib.parse(filepath)

    new_ciff = CIFF()
    new_ciff.magic = ciff_ptr.contents.magic.decode('utf-8')
    new_ciff.header_size = ciff_ptr.contents.header_size
    new_ciff.content_size = ciff_ptr.contents.content_size
    new_ciff.width = ciff_ptr.contents.width
    new_ciff.height = ciff_ptr.contents.height
    new_ciff.caption = ciff_ptr.contents.caption.decode('utf-8')
    new_ciff.tags = []
    tags_ptr = ciff_ptr.contents.tags
    if tags_ptr:
        i = 0
        while tags_ptr[i]:
            new_ciff.tags.append(tags_ptr[i].decode('utf-8'))
            i += 1
    else:
        new_ciff.tags = []
    new_ciff.pixels = []
    pixels_ptr = ciff_ptr.contents.pixels
    if pixels_ptr:
        for i in range(ciff_ptr.contents.width * ciff_ptr.contents.height):
            pixel = pixels_ptr[i]
            new_ciff.pixels.append((pixel.r, pixel.g, pixel.b))
    else:
        new_ciff.pixels = []

    new_ciff.is_valid = ciff_ptr.contents.is_valid
    lib.free.argtypes = [POINTER(CIFF_Export)]
    return new_ciff
    #print("CIFF pointer:", ciff_ptr)
    #if ciff_ptr.contents.is_valid:
    #    print("isValid:", ciff_ptr.contents.is_valid)
    #    print("Magic:", ciff_ptr.contents.magic.decode('utf-8'))
    #    print("Width:", ciff_ptr.contents.width)
    #    print("Height:", ciff_ptr.contents.height)
    #    print("Header Size:", ciff_ptr.contents.header_size)
    #    print("Content Size:", ciff_ptr.contents.content_size)
    #    print("Caption:", ciff_ptr.contents.caption.decode('utf-8'))
    #    print("Tags:")
    #    tags_ptr = ciff_ptr.contents.tags
    #    if tags_ptr:
    #        i = 0
    #        while tags_ptr[i]:
    #            print(f"  Tag {i}: {tags_ptr[i].decode('utf-8')}")
    #            i += 1
    #    else:
    #        print("  No tags found")
    #else:
    #    print("Érvénytelen CIFF fájl")
#
    #print("Macska")
