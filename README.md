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

* "[On Compressing Permutations and Adaptive Sorting](https://arxiv.org/pdf/1108.4408)" by Barbay and Navarro, which can be very useful for maintaining massive permutations in memory while allowing efficient inverse lookups. This data structure is most useful when the permutation consists of many runs of increasing values.

* [LOUDS](https://users.dcc.uchile.cl/~gnavarro/algoritmos/ps/alenex10.pdf) representation of binary tree topology, using (in theory) slightly more than two bits per tree node while providing efficient tree navigation.

Statement of public good
------------------------
This project is made possible by [The Mathematics and Informatics Institute of Ohio](#). The author gratefully acknowledges [Root Insurance Company](https://www.joinroot.com/) for providing 12 "hack days" per year for engineers to work on projects such as this one.
