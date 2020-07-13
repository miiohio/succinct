import gzip
import os
import pathlib
import pickle
from typing import List

from succinct.string_index import StringIndex


ROOT_DIR = pathlib.Path(__file__).parent


def my_func(input_file_path: pathlib.Path) -> None:
    out_raw = "raw.dat"
    out_gz = "gz.dat"
    out_idx = "idx.dat"

    take_amt = 25
    lines: List[str] = []

    with gzip.open(input_file_path, 'rt') as f:
        for line in f:
            line = line.rstrip()
            lines.append(line)
            if len(lines) == take_amt:
                break

    with open(out_raw, 'wb') as f:
        pickle.dump(lines, f)
    size = os.path.getsize(f.name)
    print(f"\tRaw size: {size}")

    with gzip.open(open(out_gz, 'wb'), 'wb') as f:
        pickle.dump(lines, f)
    size = os.path.getsize(f.name)
    print(f"\tGzipped size: {size}")
    idx = StringIndex(lines)

    with open(out_idx, 'wb') as f:
        pickle.dump(idx, f)
    size = os.path.getsize(f.name)
    print(f"\tCompressed size: {size}")

    assert len(idx) == len(lines)

    print("A")
    print(set(lines).difference(set(idx)))
    print("B")
    print(set(idx).difference(set(lines)))
    assert set(lines) == set(idx)


if __name__ == '__main__':
    my_func(ROOT_DIR / "example_1.txt.gz")
    my_func(ROOT_DIR / "example_2.txt.gz")
