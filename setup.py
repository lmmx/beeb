from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

long_description = long_description.replace("beeb_logo.png", "beeb_logo_small.png")

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
    url="https://github.com/lmmx/beeb",
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
