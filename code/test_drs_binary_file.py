from sys import argv, exit

if not len(argv) == 2:
    print("Wrong number of arguments!")
    print("Usage: python decode.py filename.dat")
    print("Exiting...")
    exit()

input_filename = argv[1]
f = open( input_filename, "rb")

i_byteword=0                  # initialize event number

while True:
    header = f.read(4)
    if header == b"TIME" or header.startswith(b"C00") or header.startswith(b'B#') or header == b'EHDR' or header.startswith(b'T#'):
        print('For byteword #', i_byteword, "Header is:", header)
    elif header == b"":
        break
    i_byteword += 1
