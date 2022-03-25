import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="terminwind",
    version="0.1.0",
    author="Yubo Wang",
    author_email="yubowang2007@gmail.com",
    description="A terminal code editor built with Textual",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HiPeople21/Terminwind",
    project_urls={
        "Bug Tracker": "https://github.com/HiPeople21/Terminwind/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["terminwind"],
    python_requires=">=3.9",
    entry_points={"console_scripts": ["terminwind = terminwind.main:main"]},
)
