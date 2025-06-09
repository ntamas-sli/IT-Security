import struct
from typing import List, Tuple, Any
import logging
from typing import List, Tuple, Optional


logger = logging.getLogger(__name__)

class CIFF:
    """
    Holds data of a CIFF image
    """

    def __init__(self,
                 magic_chars: str = "CIFF",
                 header_size_long: int = 0,
                 content_size_long: int = 0,
                 width_long: int = 0,
                 height_long: int = 0,
                 caption_string: str = "",
                 tags_list: Optional[List[str]] = None,
                 pixels_list: Optional[List[Tuple[int, int, int]]] = None
                 ):
        """
        Constructor for CIFF images

        :param magic_chars: the magic "CIFF" characters
        :param header_size_long: size of the header in bytes (8-byte-long int)
        :param content_size_long: size of content in bytes 8-byte-long int)
        :param width_long: width of the image (8-byte-long int)
        :param height_long: height of the image (8-byte-long int)
        :param caption_string: caption of the image (string)
        :param tags_list: list of tags in the image
        :param pixels_list: list of pixels to display
        """
        self._magic: str = magic_chars
        self._header_size: int = header_size_long
        self._content_size: int = content_size_long
        self._width: int = width_long
        self._height: int = height_long
        self._caption: str = caption_string

        if tags_list is None:
            self._tags: List[str] = []
        else:
            self._tags: List[str] = tags_list

        if pixels_list is None:
            self._pixels: List[Tuple[int, int, int]] = []
        else:
            self._pixels: List[Tuple[int, int, int]] = pixels_list

        self._is_valid: bool = True

    #
    # Properties
    #

    @property
    def is_valid(self) -> bool:
        """
        A flag indicating whether the the CIFF image conforms
        with the specification or not

        :return: boolean
        """
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value: bool) -> None:
        self._is_valid = value

    @property
    def magic(self) -> str:
        """
        The parsed magic characters

        :return: str
        """
        return self._magic

    @magic.setter
    def magic(self, value: str) -> None:
        self._magic = value

    @property
    def header_size(self) -> int:
        """
        The parsed header size

        :return: int
        """
        return self._header_size

    @header_size.setter
    def header_size(self, value: int) -> None:
        self._header_size = value

    @property
    def content_size(self) -> int:
        """
        The parsed content size

        :return: int
        """
        return self._content_size

    @content_size.setter
    def content_size(self, value: int) -> None:
        """
        Setter function for the content size
        """
        self._content_size = value

    @property
    def width(self) -> int:
        """
        The parsed width of the image

        :return: int
        """
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        self._width = value

    @property
    def height(self) -> int:
        """
        The parsed height of the image

        :return: int
        """
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        self._height = value

    @property
    def caption(self) -> str:
        """
        The parsed image caption

        :return: str
        """
        return self._caption

    @caption.setter
    def caption(self, value: str) -> None:
        self._caption = value

    @property
    def tags(self) -> List[str]:
        """
        The parsed list of tags

        :return: list of strings
        """
        return self._tags

    @tags.setter
    def tags(self, value: List[str]) -> None:
        self._tags = value

    @property
    def pixels(self) -> List[Tuple[int, int, int]]:
        """
        The parsed pixels

        :return: list
        """
        return self._pixels

    @pixels.setter
    def pixels(self, value: List[Tuple[int, int, int]]) -> None:
        self._pixels = value

    #
    # Static methods
    #

    @staticmethod
    def parse_ciff_file(file_path):
        """
        Parses a CIFF file and constructs the corresponding object

        :param file_path: path the to file to be parsed (string)
        :return: the parsed CIFF object
        """
        new_ciff = CIFF()
        bytes_read = 0

        # the following code can throw Exceptions at multiple lines
        try:
            with open(file_path, "rb") as ciff_file:
                # read the magic bytes
                magic = ciff_file.read(4)
                # read may not return the requested number of bytes
                if len(magic) != 4:
                    raise Exception("Invalid magic length")
                bytes_read += 4
                # decode the bytes as 4 characters
                new_ciff.magic = magic.decode('ascii')
                if new_ciff.magic != "CIFF":
                    new_ciff.is_valid = False
                    raise Exception("Invalid magic value")

                # read the header size
                h_size = ciff_file.read(8)
                if len(h_size) != 8:
                    raise Exception("Invalid h_size value")
                bytes_read += 8
                # interpret the bytes as an 8-byte-long integer
                # unpack returns a list
                new_ciff.header_size = struct.unpack("Q", h_size)[0]
                
                #TODO: maybe something is missing here

                # read the content size
                c_size = ciff_file.read(8)
                if len(c_size) != 8:
                    raise Exception("Invalid content size")
                bytes_read += 8
                # interpret the bytes as an 8-byte-long integer
                new_ciff.content_size = struct.unpack("Q", c_size)[0]
                # the content size must be in [0, 2^64 - 1]
                if new_ciff.content_size < 0 or new_ciff.content_size > (2**64)-1:
                    raise Exception("Invalid content size")

                # read the width
                width = ciff_file.read(8)
                if len(width) != 8:
                    raise Exception("Invalid width size")
                bytes_read += 8
                # interpret the bytes as an 8-byte-long integer
                new_ciff.width = struct.unpack("Q", width)[0]
                # the width must be in [0, 2^64 - 1]
                if new_ciff.width < 0 or new_ciff.width > (2**64)-1:
                    raise Exception("Invalid width value")

                # read the height
                height = ciff_file.read(8)
                if len(height) != 8:
                    raise Exception("Invalid height read size")
                bytes_read += 8
                # interpret the bytes as an 8-byte-long integer
                # HINT: check out the "q" format specifier!
                # HINT: Does it fit our purposes?
                new_ciff.height = struct.unpack("Q", height)[0]
                # the header size must be in [0, 2^64 - 1]
                if new_ciff.height < 0 or new_ciff.height > (2**64)-1:
                    raise Exception("Invalid hight value")

                #TODO: maybe something is missing here

                # read the name of the image character by character
                caption = ""
                c = ciff_file.read(1)
                if len(c) != 1:
                    raise Exception(f"No more character left in caption. Caption is: {caption}")
                bytes_read += 1
                char = c.decode('ascii')
                # read until the first '\n' (caption cannot contain '\n')
                while char != '\n':
                    # append read character to caption
                    caption += char
                    # read next character
                    c = ciff_file.read(1)
                    if len(c) != 1:
                        raise Exception(f"No more character left in caption. Caption is: {caption}")
                    bytes_read += 1
                    char = c.decode('ascii')
                new_ciff.caption = caption

                # read all the tags
                tags = list()
                # read until the end of the header
                tag = ""
                while bytes_read != new_ciff.header_size:
                    c = ciff_file.read(1)
                    if len(c) != 1:
                        raise Exception("Invalid block header size")
                    bytes_read += 1
                    char = c.decode('ascii')
                    # tags should not contain '\n'
                    if char == '\n':
                        raise Exception("Invalid image")
                    # tags are separated by terminating nulls
                    tag += char
                    if char == '\0':
                        tags.append(tag)
                        tag = ""
                    # the very last character in the header must be a '\0'
                    if (bytes_read == new_ciff.header_size) and char != '\0':
                        raise Exception("Header last character problem")
                # all tags must end with '\0'
                for tag in tags:
                    if tag[-1] != '\0':
                        raise Exception("Tag terminating character error")
                new_ciff.tags = tag

                # read the pixels
                while bytes_read < new_ciff.header_size+new_ciff.content_size:
                    c = ciff_file.read(3)
                    if len(c) != 3:
                        raise Exception("Invalid content: Pixel read error")
                    bytes_read += 3
                    pixel = struct.unpack("BBB", c)  # type: ignore  # generic function that return the correct type in this case
                    new_ciff.pixels.append(pixel)

                # we should have reached the end of the file
                c = ciff_file.read(1)
                if len(c) == 1:
                    raise Exception("File total length error")

        except Exception as e:
            logger.error(f"Exception: {e}")
            new_ciff.is_valid = False

        return new_ciff
