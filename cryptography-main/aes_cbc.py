import sys, getopt
from Crypto import Random
from Crypto.Util import Padding
from Crypto.Cipher import AES
from Crypto.Protocol import KDF


# ------ CONFIG ------
TEST = True
# --------------------

operation = 'enc'
passphrase = ''
ifile_name = './test_plaintext_1.txt'
ofile_name = ''

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hedp:i:o:')
except getopt.GetoptError:
    print('Usage: aes_cbc.py [-e|-d] -p <passphrase> -i <inputfile> -o <outputfile>')
    sys.exit(1)

for opt, arg in opts:
    if opt == '-h':
        print('Usage: aes_cbc.py [-e|-d] -p <passphrase> -i <inputfile> -o <outputfile>')
        sys.exit(0)
    elif opt == '-e':
        operation = 'enc'    
    elif opt == '-d':
        operation = 'dec'    
    elif opt == '-p':
        passphrase = arg
    elif opt == '-i':
        ifile_name = arg
    elif opt == '-o':
        ofile_name = arg
    
if not ifile_name:
    print('Error: Name of input file is missing.')
    sys.exit(1)

if not ofile_name:
    print('Error: Name of output file is missing.')
    sys.exit(1)

if not passphrase:
    print('Error: No passphrase is given.')
    sys.exit(1)

# encryption
if operation == 'enc': 
    print('Encrypting...', end='')
	
    # generate a salt for key derivation and an IV for encryption in CBC mode
    # (random values if not in test mode)
    if TEST:
        salt = b'saltsaltsaltsalt'    # a 16-byte test salt
        iv = b'iviviviviviviviv'    # a 16-byte test IV        
    else:
        salt = Random.get_random_bytes(16)    # a 16-byte random salt
        iv = Random.get_random_bytes(16)    # a 16-byte random IV

    # read the content of the input file into a variable called plaintext
    with open(ifile_name, 'rb') as f:
        plaintext = f.read()

    # apply PKCS7 style padding on the plaintext
    # TODO: padded_plaintext = Padding.pad(__, __, style=__)

        padded_plaintext = Padding.pad(plaintext, AES.block_size, style='pkcs7')

    # derive a 32-byte encryption key from the passphrase 
    # using PBKDF2 with the salt and iteration count 100000
    # TODO: key = KDF.PBKDF2(__, __, count=__, dkLen=__)

        key = KDF.PBKDF2(passphrase, salt, count=100000, dkLen=32)

    # create a AES-CBC cipher object using the key and the IV
    # TODO: aes_cbc = AES.new(__, __, __)

        aes_cbc = AES.new(key, AES.MODE_CBC, iv)

    # encrypt the padded plaintext to produce a ciphertext
    # TODO: ciphertext = __.encrypt(__)

        ciphertext = aes_cbc.encrypt(padded_plaintext)

    # write out the random salt used for key derivation, the IV,
    # and the ciphertext to the output file
    with open(ofile_name, "wb") as f:
        f.write(salt)
        f.write(iv)
        f.write(ciphertext)

    print('Done.')
    print('Your solution to Challenge 1: ' + ciphertext[-16:].hex())
    print('Hint: The correct solution starts with 3b256f.')

# decryption
else:
    print('Decrypting...', end='')

    # read the salt, the IV, and the ciphertext from the input file
    with open(ifile_name, 'rb') as f:
        salt = f.read(16)
        iv = f.read(16)
        ciphertext = f.read()
    
    # derive the 32-byte key from the passphrase 
    # using PBKDF2 with the salt and iteration count 100000
    # TODO: key = ...

        key = KDF.PBKDF2(passphrase, salt, count=100000, dkLen=32)

    # create an AES-CBC cipher object for decrypting the ciphertext 
    # TODO: aes_cbc = ... 

        aes_cbc = AES.new(key, AES.MODE_CBC, iv)
	
    # decrypt the ciphertext and remove padding
    try:
        # TODO: padded_plaintext = __.decrypt(__)
        
        padded_plaintext = aes_cbc.decrypt(ciphertext)

        # TODO: plaintext = __.unpad(__, __, style=__)

        plaintext = Padding.unpad(padded_plaintext, AES.block_size, style='pkcs7')
        
        # pass # TODO: remove this line!

    except ValueError:
        print('Error: Decryption failed.')
        sys.exit(1)

    # write out the plaintext into the output file
    with open(ofile_name, "wb") as f:
        f.write(plaintext)

    print('Done.')
    print('Your solution to Challenge 2: ' + plaintext[:16].hex())	
    print('Hint: The correct solution starts with 537475.')

