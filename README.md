Succinct
========

Succinct, compact, and compressed data structures for data-intensive applications.

Notable features
----------------

* State of the art [broadword](http://vigna.di.unimi.it/papers.php#VigBIRSQ) [select](https://en.wikipedia.org/wiki/Succinct_data_structure#Succinct_dictionaries) implementation based on Sebastiano
Vigna's [fastutil](http://dsiutils.di.unimi.it/docs/it/unimi/dsi/bits/Fast.html#select(long,int))
library.

* "[Space-Efficient, High-Performance Rank and Select Structures on Uncompressed Bit Sequences](https://link.springer.com/chapter/10.1007/978-3-642-38527-8_15)" that supports bit arrays with up to `2^64` bits. This is a data structure that endows Python's [bitarray](https://github.com/ilanschnell/bitarray) data structure with the following operations:
    * `rank(i: int) -> int`: The number of one bits to the left of, and including, the `i`th position.

    * `rank_zero(i: int) -> int`: The number of zero bits to the left of, and including, the `i`th position.

    * `select(bit_rank: int) -> int`: The index of the left-most bit in the `bitarray` whose rank is `bit_rank`.

    * `select_zero(bit_rank_zero: int) -> int`: The index of the left-most bit in the `bitarray` whose rank_zero is `bit_rank`. The current implementation of `select_zero` is not as efficient as the implementation of `select`, as it uses a binary search over `rank_zero` rather than a sophisticated data structure. This may change in the future.

* [Elias-Fano representation](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.219.2439&rep=rep1&type=pdf) of monotone sequences of natural numbers. Using this encoding, "an element occupies a number of bits bounded by two plus the logarithm of the average gap" ([source](http://sux4j.di.unimi.it/docs/it/unimi/dsi/sux4j/util/EliasFanoMonotoneLongBigList.html)). This can be an excellent data structure for representing lists of monotonically-increasing natural numbers. Applications include inverted indexes, pointers into massive arrays, etc. See [this blog post](https://www.antoniomallia.it/sorted-integers-compression-with-elias-fano-encoding.html) for more information.

* Compressed bit array representations supporting `rank`, `rank_zero`, `select`,
and `select_zero`:

    * `CompressedRunsBitArray`: A compressed bit array representation that is effective for compactly representing
    bit sequences consisting of many runs of consecutive 1s and 0s (i.e., low
    first-order entropy). It supports reasonably performant `select` and `select_zero`, and currently supports a
    less-performant but correct `rank` and `rank_zero` operations. Future work will
    make them all faster. This data structure is described in Section 4.4.3
    "Bitvectors with Runs" of Gonzalo Navarro's _Compact Data Structures_ book.

    * `EliasFanoBitArray`: A compressed bit array representation that
    uses Elias-Fano representation of monotone sequences of natural numbers to store
    the locations of 1 bits in sparse bit sequences. It supports `rank`, `rank_zero`,
    `select`, and `select_zero`. This is described in Section 4.3 "Very Sparse Bitvectors"
    of Gonzalo Navarro's _Compact Data Structures_ book. (NOTE: Some implementation
    details vary from the description in the book.)

    * `RunLengthEncodedBitArray`: A compressed bit array representation using
    rudimentary [run-length encoding](https://en.wikipedia.org/wiki/Run-length_encoding)
    to encode intervals of contiguous runs of 1's.

* "[On Compressing Permutations and Adaptive Sorting](https://arxiv.org/pdf/1108.4408)" by Barbay and Navarro, which can be very useful for maintaining massive permutations in memory while allowing efficient inverse lookups. This data structure is most useful when the permutation consists of many runs of increasing values.

* [LOUDS](https://users.dcc.uchile.cl/~gnavarro/algoritmos/ps/alenex10.pdf) representation of binary tree topology, using (in theory) slightly more than two bits per tree node while providing efficient tree navigation.

* (In progress) `StringIndex`: A potentially novel (research TBD) compressed
succint string self-index capable of representing multisets of strings. You can
think of it as a compression algorithm that provides random access to any string
in the multiset, where the index of each string is defined according to an
implicit minimal perfect hash function. Preliminary experiments indicate that
it achieves space savings that are comparable to `gzip` compression; index sizes
are within 1.5x to 4x the size of the gzipped text.

    Future work will improve the runtime performance of the index, as well as add
    search operations that one would expect from a succinct string self-index.
    This Python implementation is based on a never-released Scala prototype
    that I made several years ago, which does feature those operations.

Installation
---------------
At the command line:
```bash
$ pip install succinct
```

Alternatively, you can install `succinct` from source by cloning this repo and running the provided `setup.sh` script.

Version History
---------------
**0.0.7**: (Release 9/24/2020)
- Fix bug in `Poppy.select` that was due to accidentally truncating the binary
search within 64-byte basic blocks. The unit test `test_select_binary_search_bug_is_not_present_2020_09_06`
was added to witness the bug fix.

- Added the compressed bit sequence data structures `RunLengthEncodedBitArray`,
`EliasFanoBitArray`, and `CompressedRunsBitArray`.

- Sprinkled some assertions throughout the codebase for good measure.

- Added the (work in progress) `StringIndex` succinct string self-index data
structure. Correctness and compactness appear to be good, but some performance
tuning is in order. Stick around to see what the future holds. I have big plans
for this data structure.

- Allow `EliasFano` constructor to take a prescribed number of bits to use for
recording lower-order bits in a special bit vector. Changing this value for a
given bit vector may result in better compression ratios.

Statement of public good
------------------------
This project is made possible by [The Mathematics and Informatics Institute of Ohio](#). The author gratefully acknowledges [Root Insurance Company](https://www.joinroot.com/) for providing 12 "hack days" per year for engineers to work on projects such as this one.
