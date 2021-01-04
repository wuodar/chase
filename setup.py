import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chase-pkg",
    version="0.0.2",
    author="Kacper Włodarczyk",
    description="Chase package.",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wuodar/chase",
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
)