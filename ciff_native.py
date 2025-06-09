import ctypes
from ctypes import c_char_p, Structure, POINTER, c_int64, c_bool, c_uint8

# Definiáljuk a struct-okat Pythonban is
class RGBPixel(ctypes.Structure):
    _fields_ = [("r", c_uint8),
                ("g", c_uint8),
                ("b", c_uint8)]

class CIFF(Structure):
    _fields_ = [
        ("magic", ctypes.c_char_p),
        ("header_size", c_int64),
        ("content_size", c_int64),
        ("width", c_int64),
        ("height", c_int64),
        ("caption", ctypes.c_char_p),
        ("tags", POINTER(c_char_p)),        # pointer tömb (feltételezve, hogy így van exportálva)
        ("pixels", POINTER(RGBPixel)),      # pointer pixel tömbhöz
        ("is_valid", c_bool)
    ]

# Betöltjük a DLL-t
lib = ctypes.cdll.LoadLibrary("./ciff_parser.dll")

# Beállítjuk a függvény típusát
lib.parse.argtypes = [c_char_p]
lib.parse.restype = POINTER(CIFF)

# Meghívjuk
filepath = b"example.ciff"  # bináris string!
ciff_ptr = lib.parse(filepath)

if ciff_ptr.contents.is_valid:
    print("Magic:", ciff_ptr.contents.magic.decode('ascii'))
    print("Caption:", ciff_ptr.contents.caption.decode('utf-8'))
    # stb.
else:
    print("Érvénytelen CIFF fájl")
