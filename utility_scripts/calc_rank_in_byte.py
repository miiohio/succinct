from bitarray import bitarray


"""
Utility script for pre-calculating succinct.bits.RANK_IN_BYTE
"""

result = [0] * 256 * 8

for b in range(0, 256):
    a = bitarray()
    a.frombytes(bytes([b]))
    cur_rank = 0
    for i, bit in enumerate(a):
        if bit:
            cur_rank += 1
        pos = 256 * i + b
        result[pos] = cur_rank

print(result)
print("Done.")
