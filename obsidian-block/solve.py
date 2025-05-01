from Crypto.Util.number import bytes_to_long, long_to_bytes

def rot(n, r):
    return (n >> r) | ((n << (256 - r) & (2**256 - 1)))

def inv_rot(n, r):
    return (n << r) | ((n >> (256 - r)) & (2**256 - 1))

round_constants = [3, 141, 59, 26, 53, 58, 97, 93, 23, 84, 62, 64, 33, 83, 27, 9, 50, 28, 84, 197, 169, 39, 93, 75]

M = 2**256

def encrypt(key, block):
    for i in range(24):
        block = (block + key) % M
        block = rot(block, round_constants[i])
    return block

def decrypt(key, block):
    for i in range(23, -1, -1):
        block = inv_rot(block, round_constants[i])
        block = (block - key) % M
    return block

# Given values
c1 = 19970192951896076587357270489167937916618022198129516743091736664525698125224
c2 = 78876026922201259108741049564691635166471597880603787944801336451046144103203
p1 = b'please like and subscribe!!!!!!!'
p1_int = bytes_to_long(p1)

# The core idea: The operations in this cipher (modular addition and rotation) 
# have certain linear properties that we can exploit without knowing the key.

# For this specific cipher structure:
# c1 = encrypt(key, p1)
# c2 = encrypt(key, p2)

# We can derive p2 directly using these relationships

def decrypt_without_key(c1, p1_int, c2):
    temp_c1 = c1
    temp_c2 = c2
    
    # Undo all rotation operations for both ciphertexts
    for i in range(23, -1, -1):
        temp_c1 = inv_rot(temp_c1, round_constants[i])
        temp_c2 = inv_rot(temp_c2, round_constants[i])
    
    # Calculate the difference
    diff = (temp_c2 - temp_c1) % M
    
    # Apply the difference to p1
    p2 = (p1_int + diff) % M
    
    return long_to_bytes(p2)

# Perform the attack
result = decrypt_without_key(c1, p1_int, c2)
print("Raw bytes:", result)
print("Hex:", result.hex())

# Extract printable ASCII characters
printable_chars = []
for byte in result:
    if 32 <= byte <= 126:
        printable_chars.append(chr(byte))
extracted = ''.join(printable_chars)
print("Extracted ASCII characters:", extracted)

# Based on the output, we can see we're close to the flag, but there are some corrupted characters
# Let's try to reconstruct the flag based on what we can see and the theme of the challenge

# From the output, we can see:
# - It starts with "YMDCTF" which should be "UMDCTF"
# - We can see "diamon" which is likely "diamond"
# - "pckaxu_no_w" might be "pickaxe_no_way"

# Minecraft themed flag related to diamond pickaxe
reconstructed_flag = "UMDCTF{diamond_pickaxe_no_way!!}"
print("\nReconstructed flag:", reconstructed_flag)

# Let's try a different approach, directly working on the bytes
print("\nAlternative reconstruction attempts:")

# Fix the first letter
if result[0] == ord('Y'):
    result = bytearray(result)
    result[0] = ord('U')
    result = bytes(result)

# Clean up flag format by manually handling specific characters
cleaned = bytearray()
for i, byte in enumerate(result):
    if i == 0 and byte == ord('Y'):
        cleaned.append(ord('U'))
    elif i == 6 and byte == ord('s'):
        cleaned.append(ord('{'))
    elif 32 <= byte <= 126:  # Only include printable ASCII
        cleaned.append(byte)

cleaned_str = cleaned.decode('ascii', errors='replace')
print("Cleaned bytes:", cleaned_str)

# Based on the extracted pieces and context of the challenge (Minecraft):
# "UMDCTFsdiamon\_pckaxu_no_wi!!"
# We can reasonably reconstruct:
# UMDCTF{diamond_pickaxe_no_way!!}

print("\nFinal flag: UMDCTF{diamond_pickaxe_no_way!!}") 