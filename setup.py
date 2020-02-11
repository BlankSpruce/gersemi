from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="gersemi",
    version="0.1.0",
    author="Blank Spruce",
    author_email="blankspruce@protonmail.com",
    description="A formatter to make your CMake code the real treasure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BlankSpruce/gersemi",
    packages=find_packages(include=["gersemi", "gersemi.*"]),
    package_data={"gersemi": ["cmake.lark"]},
    install_requires=["lark-parser==0.8"],
    python_requires=">=3.7",
    entry_points={"console_scripts": ["gersemi = gersemi.__main__:main"]},
    license="MPL 2.0",
)
