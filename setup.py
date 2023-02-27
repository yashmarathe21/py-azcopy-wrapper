from setuptools import setup  # type: ignore

with open("README.md") as f:
    long_description = f.read()


setup(
    name="azcopy_wrapper",
    version="0.0.6",
    description=("A simple AzCopy wrapper to transfer data"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/yashmarathe21/py-azcopy-wrapper",
    author="Kurien Zacharia, Yash Marathe",
    author_email="yashmarathe21@gmail.com",
    keywords="azcopy wrapper python azure storage bulk upload blob sync copy",
    license="MIT",
    python_requires=">=3.6",
    packages=["azcopy_wrapper", "azcopy_wrapper/utils/"],
    install_requires=[],
)
