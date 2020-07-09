# from bitarray import bitarray
# from succinct.eliasfano import EliasFano


# def test_elias_fano_example_1() -> None:
#     values = [2, 3, 5, 7, 11, 13, 24]
#     ef = EliasFano(values, num_values=len(values), max_value=max(values))

#     # bottom 3 bits of each number
#     expected_lower_bits = bitarray('010011101111011101000')

#     assert ef._lower_bits == expected_lower_bits
