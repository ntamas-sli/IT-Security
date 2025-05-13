import sys, getopt, getpass
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import PKCS1_PSS
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Util import Padding
from Crypto import Random

# ------ CONFIG ------
TEST = True
# --------------------

def save_publickey(pubkey, pubkeyfile):
    with open(pubkeyfile, 'wb') as f:
        f.write(pubkey.export_key(format='PEM'))

def load_publickey(pubkeyfile):
    with open(pubkeyfile, 'rb') as f:
        pubkeystr = f.read()
    try:
        return RSA.import_key(pubkeystr)
    except ValueError:
        print('Error: Cannot import public key from file ' + pubkeyfile)
        sys.exit(1)

def save_keypair(keypair, privkeyfile):
    # passphrase = input('Enter a passphrase to protect the saved private key: ')
    passphrase = getpass.getpass('Enter a passphrase to protect the saved private key: ')
    with open(privkeyfile, 'wb') as f:
        f.write(keypair.export_key(format='PEM', passphrase=passphrase))

def load_keypair(privkeyfile):
    #passphrase = input('Enter a passphrase to decode the saved private key: ')
    passphrase = getpass.getpass('Enter a passphrase to decode the saved private key: ')
    with open(privkeyfile, 'rb') as f:
        keypairstr = f.read()
    try:
        return RSA.import_key(keypairstr, passphrase=passphrase)
    except ValueError:
        print('Error: Cannot import private key from file ' + privkeyfile)
        sys.exit(1)

def test_random(nbytes):
    return b'\x00'*nbytes

# ----------------------------------
# processing command line parameters
# ----------------------------------

operation = ''
pubkeyfile = ''
privkeyfile = ''
inputfile = ''
outputfile = ''
sign = False

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hkedp:s:i:o:')
except getopt.GetoptError:
    print('Usage:')
    print('  - RSA key pair generation:')
    print('    hybrid.py -k -p <pubkeyfile> -s <privkeyfile>')
    print('  - encryption with optional signature generation:')
    print('    hybrid.py -e -p <pubkeyfile> [-s <privkeyfile>] -i <inputfile> -o <outputfile>')
    print('  - decryption with optional signature verification:')
    print('    hybrid.py -d -s <privkeyfile> [-p <pubkeyfile>] -i <inputfile> -o <outputfile>')
    sys.exit(1)

for opt, arg in opts:
    if opt == '-h':
        print('Usage:')
        print('  - RSA key pair generation:')
        print('    hybrid.py -k -p <pubkeyfile> -s <privkeyfile>')
        print('  - encryption with optional signature generation:')
        print('    hybrid.py -e -p <pubkeyfile> [-s <privkeyfile>] -i <inputfile> -o <outputfile>')
        print('  - decryption with optional signature verification:')
        print('    hybrid.py -d -s <privkeyfile> [-p <pubkeyfile>] -i <inputfile> -o <outputfile>')
        sys.exit(0)
    elif opt == '-k':
        operation = 'kpg'
    elif opt == '-e':
        operation = 'enc'    
    elif opt == '-d':
        operation = 'dec'    
    elif opt == '-p':
        pubkeyfile = arg
    elif opt == '-s':
        privkeyfile = arg
    elif opt == '-i':
        inputfile = arg
    elif opt == '-o':
        outputfile = arg

if not operation:
    print('Error: Operation must be -k (for key pair generation) or -e (for encryption) or -d (for decryption).')
    sys.exit(1)
    
if (not pubkeyfile) and (operation == 'enc' or operation == 'kpg'):
    print('Error: Name of the public key file is missing.')
    sys.exit(1)

if (not privkeyfile) and (operation == 'dec' or operation == 'kpg'):
    print('Error: Name of the private key file is missing.')
    sys.exit(1)

if (not inputfile) and (operation == 'enc' or operation == 'dec'):
    print('Error: Name of input file is missing.')
    sys.exit(1)

if (not outputfile) and (operation == 'enc' or operation == 'dec'):
    print('Error: Name of output file is missing.')
    sys.exit(1)

if (operation == 'enc') and privkeyfile: 
    sign = True

# -------------------
# key pair generation
# -------------------

if operation == 'kpg': 
    print('Generating a new 2048-bit RSA key pair...')
    keypair = RSA.generate(2048)
    save_publickey(keypair.publickey(), pubkeyfile)
    save_keypair(keypair, privkeyfile)
    print('Done.')

# ----------
# encryption
# ----------

elif operation == 'enc': 
    print('Encrypting...')

    # load the public key from the public key file and 
    pubkey = load_publickey(pubkeyfile)

    # create an RSA cipher object
    # (in TEST mode, we want to use our test random number generator)
    if TEST: 
        RSAcipher = PKCS1_OAEP.new(pubkey, randfunc=test_random)
    else:
        RSAcipher = PKCS1_OAEP.new(pubkey)

    # generate a symmetric key and an IV (random values if not in test mode)
    if TEST:
        symkey = b'testtesttesttesttesttesttesttest'  # a 32-byte test key
        iv = b'iviviviviviviviv'  # a 16-byte test IV        
    else:
        # TODO: symkey = ...   # a 32-byte random key
        symkey = Random.get_random_bytes(32)
        # TODO: iv = ...   # a 16-byte random IV
        iv = Random.get_random_bytes(16)

    # create an AES-CBC cipher object with the generated key and IV
    # TODO: AEScipher = ...
    AEScipher = AES.new(symkey, AES.MODE_CBC, iv)

    # read the plaintext from the input file
    with open(inputfile, 'rb') as f: 
        plaintext = f.read()

    # apply PKCS7 padding on the plaintext
    # TODO: padded_plaintext = ...
    padded_plaintext = Padding.pad(plaintext, AES.block_size)
	
    # encrypt the padded plaintext with the AES-CBC cipher
    # TODO: ciphertext = ...
    ciphertext = AEScipher.encrypt(padded_plaintext)

    #encrypt the AES key with the RSA cipher
    # TODO: encsymkey = ... 
    encsymkey = RSAcipher.encrypt(symkey)

    # compute signature if needed
    if sign:
        keypair = load_keypair(privkeyfile)
        signer = PKCS1_PSS.new(keypair)
        hashfn = SHA256.new()
        hashfn.update(encsymkey+iv+ciphertext)
        signature = signer.sign(hashfn)

    # create a dictionary to store the encrypted AES key, the IV, the ciphertext, and the signature
    hybrid_struct = {}
    hybrid_struct['ENCRYPTED AES KEY'] = b64encode(encsymkey).decode('ascii')
    hybrid_struct['IV FOR CBC MODE'] = b64encode(iv).decode('ascii')
    hybrid_struct['CIPHERTEXT'] = b64encode(ciphertext).decode('ascii')
    if sign: hybrid_struct['SIGNATURE'] = b64encode(signature).decode('ascii')

    # write out the dictionary in json format
    with open(outputfile, 'w') as f:
        f.write(json.dumps(hybrid_struct))

    print('Done.')
    print('Your solution to Challenge 3: ' + ciphertext[:16].hex())
    print('Hint: The correct solution starts with a0a0a9.')

# ----------
# decryption
# ----------

elif operation == 'dec':
    print('Decrypting...')

    # read and parse the input
    encsymkey = b''
    iv = b''
    ciphertext = b''
    signature = b''
    sign = False

    with open(inputfile, 'r') as f: 
        hybrid_struct = json.loads(f.read())

    if 'ENCRYPTED AES KEY' in hybrid_struct:
        encsymkey = b64decode(hybrid_struct['ENCRYPTED AES KEY'].encode('ascii'))
    if 'IV FOR CBC MODE' in hybrid_struct:
        iv = b64decode(hybrid_struct['IV FOR CBC MODE'].encode('ascii'))
    if 'CIPHERTEXT' in hybrid_struct:
        ciphertext = b64decode(hybrid_struct['CIPHERTEXT'].encode('ascii'))
    if 'SIGNATURE' in hybrid_struct:
        signature = b64decode(hybrid_struct['SIGNATURE'].encode('ascii'))
        sign = True

    if (not encsymkey) or (not iv) or (not ciphertext):
        print('Error: Could not parse content of input file ' + inputfile)
        sys.exit(1)

    if sign and (not pubkeyfile):
        print('Error: Public key file is missing, signature cannot be verified.')
        sys.exit(1)

    # verify signature if needed
    if sign:
        pubkey = load_publickey(pubkeyfile)
        # TODO: verifier = ...
        verifier = PKCS1_PSS.new(pubkey)
        # TODO: hashfn = ...
        hashfn = SHA256.new()
        # TODO: hashfn.update(__)
        hashfn.update(encsymkey+iv+ciphertext)
        # TODO: if verifier.verify(__, __) == True:
        if verifier.verify(hashfn, signature) == True:
            print('Signature verification is successful.')
        else:
            print('Signature verification is failed.')
            yn = input('Do you want to continue (y/n)? ')
            if yn != 'y': 
                sys.exit(1)

    # load the private key from the private key file and 
    # create the RSA cipher object
    keypair = load_keypair(privkeyfile)
    # TODO: RSAcipher = ...
    RSAcipher = PKCS1_OAEP.new(keypair)

    #decrypt the AES key
    try:
        # TODO: symkey = ... 
        symkey = RSAcipher.decrypt(encsymkey)
    except ValueError:
        print('Error: Decryption of AES key is failed.')
        sys.exit(1)

    #create the AES-CBC cipher object
    # TODO: AEScipher = ...  
    AEScipher = AES.new(symkey, AES.MODE_CBC, iv) 
	
    # decrypt the ciphertext and remove padding
    try:
        # TODO: padded_plaintext = ...
        padded_plaintext = AEScipher.decrypt(ciphertext)
        # TODO: plaintext = ...
        plaintext = Padding.unpad(padded_plaintext, AES.block_size)
    except ValueError:
        print('Error: Decryption of the ciphertext is failed.')
        sys.exit(1)

    # write out the plaintext into the output file
    with open(outputfile, 'wb') as f:
        f.write(plaintext)
	
    print('Done.')
    print('Your solution to Challenge 4: ' + plaintext[-16:].hex())
    print('Hint: The correct solution starts with 6f6620.')
