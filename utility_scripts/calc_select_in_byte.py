from bitarray import bitarray


"""
Utility script for pre-calculating succinct.bits.SELECT_IN_BYTE
"""

result = [-1] * 256 * 8

for b in range(0, 256):
    a = bitarray()
    a.frombytes(bytes([b]))
    cur_rank = 0
    for i, bit in enumerate(a):
        if bit:
            pos = cur_rank * 256 + b
            result[pos] = i
            cur_rank += 1

print(result)
print("Done.")
