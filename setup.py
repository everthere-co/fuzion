import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fuzion",
    version="0.0.1",
    author="Gabriel Amram",
    author_email="gabriel@everthere.co",
    description="A python API for Freeman's Fuzion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/everthere-co/fuzion",
    packages=setuptools.find_packages(),
    install_requires=["requests"],
    python_requires=">=3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
