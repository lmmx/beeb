from setuptools import setup, find_packages
import re

gh_handle = "lmmx/beeb"
gh_raw_url = "https://raw.githubusercontent.com"

with open("README.md", "r") as fh:
    long_description = fh.read()

# Change markdown image tags to HTML for PyPI
md_img_tagger = re.compile(r"\n!\[\]\((.*)\)")
long_description = md_img_tagger.split(long_description)
long_description[1] = f'\n<img src="{gh_raw_url}/{gh_handle}/master/{long_description[1]}"/>'
long_description = "".join(long_description)

with open("requirements.txt", "r") as fh:
    reqs = fh.read().splitlines()

def local_scheme(version):
    return ""

def version_scheme(version):
    return version.tag.base_version

setup(
    name="beeb",
    author="Louis Maddox",
    author_email="louismmx@gmail.com",
    description=(
        "A modern interface to the BBC Sounds radio catalogue"
    ),
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{gh_handle}",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    include_package_data=True,
    use_scm_version={
        "write_to": "version.py",
        "version_scheme": version_scheme,
        "local_scheme": local_scheme,
    },
    setup_requires=["setuptools_scm"],
    install_requires=reqs,
    python_requires=">=3",
)
