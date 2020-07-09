Succinct
========

Succinct, compact, and compressed data structures for data-intensive applications.

Notable features
----------------

* State of the art [broadword](http://vigna.di.unimi.it/papers.php#VigBIRSQ) [select](https://en.wikipedia.org/wiki/Succinct_data_structure#Succinct_dictionaries) implementation based on Sebastiano
Vigna's [fastutil](http://dsiutils.di.unimi.it/docs/it/unimi/dsi/bits/Fast.html#select(long,int))
library.

* A full implementation of "[Space-Efficient, High-Performance Rank and Select Structures on Uncompressed Bit Sequences](https://link.springer.com/chapter/10.1007/978-3-642-38527-8_15)" that supports bit arrays with up to `2^64` bits. 

* An implementation of [Elias-Fano representation](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.219.2439&rep=rep1&type=pdf) of monotone sequences of natural numbers. Using this encoding, "an element occupies a number of bits bounded by two plus the logarithm of the average gap" ([source](http://sux4j.di.unimi.it/docs/it/unimi/dsi/sux4j/util/EliasFanoMonotoneLongBigList.html)).

* (Coming soon): An implementation of "[On Compressing Permutations and Adaptive Sorting](https://arxiv.org/pdf/1108.4408)" by Barbay and Navarro, which can be very useful for maintaining massive permutations in memory while allowing efficient inverse lookups.

Statement of public good
------------------------
This project is made possible by [The Mathematics and Informatics Institute of Ohio](#). The author gratefully acknowledges [Root Insurance Company](https://www.joinroot.com/) for providing 12 "hack days" per year for engineers to work on projects such as this one.
