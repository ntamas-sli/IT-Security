import sys, getopt

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hedp:i:o:')
except getopt.GetoptError:
    print('Usage: aes_cbc.py [-e|-d] -p <passphrase> -i <inputfile> -o <outputfile>')
    sys.exit(1)

print('opts:', opts)
print('args:', args)
for opt, arg in opts:
    print(f'opt: {opt}, arg: {arg}')