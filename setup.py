import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="classutil",
    version="2.0.2",
    description="Classutil scraper for UNSW.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/lecafard/classutil",
    author="tom nguyen",
    author_email="hi@tomn.me",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"    
    ],
    packages=["classutil"],
    keywords="unsw classutil scraper",
    include_package_data=True,
    install_requires=["aiohttp", "python-dateutil", "beautifulsoup4"],
    python_requires=">=3"
)

