from setuptools import setup, find_namespace_packages


with open("succinct/VERSION") as version_file:
    version = version_file.read().strip()

kwds = {}
try:
    kwds['long_description'] = open('README.md').read()
    kwds['long_description_content_type'] = 'text/markdown'
except IOError:
    pass

setup(
    name="succinct",
    version=version,
    author="William Harvey",
    author_email="drwjharvey@gmail.com",
    description="Succinct, compact, and compressed data structures for data-intensive applications",
    url="https://github.com/miiohio/succinct",
    packages=["succinct"] + find_namespace_packages(include=["succinct.*"]),
    package_data={"succinct": ["VERSION", "py.typed"]},
    install_requires=[
        "bitarray >= 1.3.0",
        "typing_extensions >= 3.7"
    ],
    **kwds
)
