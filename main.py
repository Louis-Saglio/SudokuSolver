from genetic import GeneticEngine
from grids import *
from sudoku import Sudoku


def main():
    given_cells = empty
    engine = GeneticEngine(individual_class=Sudoku, population_size=1000, given_cells=given_cells)
    print("\n", engine.run(), sep="")


if __name__ == "__main__":
    main()
