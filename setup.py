from setuptools import setup, find_namespace_packages


with open("succinct/VERSION") as version_file:
    version = version_file.read().strip()

setup(
    name="succinct",
    version=version,
    author="William Harvey",
    description="Succinct, compact, and compressed data structures for data-intensive applications",
    url="https://github.com/miiohio/succinct",
    python_requires=">=3.7.6",
    packages=["succinct"] + find_namespace_packages(include=["succinct.*"]),
    package_data={"succinct": ["VERSION", "py.typed"]},
    install_requires=[],
)
