import os
from setuptools import setup, find_packages


HERE = os.path.dirname(os.path.realpath(__file__))

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

about = {}
with open(os.path.join(HERE, "gersemi", "__version__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)  # pylint: disable=exec-used

setup(
    name=about["__title__"],
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about["__url__"],
    packages=find_packages(include=["gersemi", "gersemi.*"]),
    package_data={"gersemi": ["cmake.lark", "builtin_commands"]},
    install_requires=[
        "appdirs",
        "dataclasses",
        "lark>=1.0",
        "pyyaml>=5,<7",
    ],
    extras_requires=["colorama>=0.4"],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["gersemi = gersemi.__main__:main"]},
    license=about["__license__"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
