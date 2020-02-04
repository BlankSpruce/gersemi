from setuptools import setup, find_packages

setup(
    name="gersemi",
    version="0.1.0",
    packages=find_packages(include=["gersemi", "gersemi.*"]),
    package_data={"gersemi": ["cmake.lark"]},
    entry_points={"console_scripts": ["gersemi = gersemi.__main__:main"]},
    install_requires=["lark-parser==0.8"],
    python_requires=">=3.7",
    author="Blank Spruce",
    description="Tool to format CMake code",
    license="MPL 2.0",
    url="https://github.com/BlankSpruce/gersemi",
)
