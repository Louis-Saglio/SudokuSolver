from time import time

from genetic import GeneticEngine
from grids import *
from sudoku import Sudoku


def main():
    start = time()
    engine = GeneticEngine(individual_class=Sudoku, population_size=1000, given_cells=small_6x6_112)
    best_solution, stats = engine.run()
    print(round(time() - start, 2))
    engine.save_stats_to_file(stats)
    print(best_solution, sep="")


if __name__ == "__main__":
    main()


# 25 : 13.12 16.46 71.85 11.86 69.44 35.41 15.80 52.88 37.83 15.52
# 10 : 11.54 02.46 26.81 12.73 40.31 88.09 32.24 07.72 11.01 21.59
# 5  : 25.72 57.58 07.48 76.01 51.21 153.1 117.5 102.6 39.32 21.15
# 15 : 10.91 29.69 61.01 48.23 168.9 04.57 20.91 58.85 05.05 33.05
