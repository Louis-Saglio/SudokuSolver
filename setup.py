import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="SudokuSolver",
    version="1.0.0",
    description="Solve Sudoku grids using a genetic algorithm",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Louis-Saglio/SudokuSolver",
    author="Louis Saglio",
    author_email="louis.saglio@ynov.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["SudokuSolver"],
    include_package_data=True,
    install_requires=[],
)