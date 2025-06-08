from ciff import CIFF
from os import listdir
from os.path import join, extsep

for test_vector in sorted(
        [f for f in listdir("test-vectors")],
        key=lambda f: int(
            f.replace("test", "").rsplit(extsep, 1)[0].rsplit(None, 1)[-1]
        )
):
    try:
        ciff_file = CIFF.parse_ciff_file(join("test-vectors", test_vector))
        if ciff_file.is_valid:
            print(test_vector + "\t is detected as \tVALID")
        else:
            print(test_vector + "\t is detected as \tINVALID")
    except Exception as e:
        print("Error processing " + test_vector)
        print(e)
