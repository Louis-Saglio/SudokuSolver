from genetic import GeneticEngine
from grids import *
from sudoku import Sudoku


def main():
    engine = GeneticEngine(individual_class=Sudoku, population_size=1000, given_cells=small_6x6_112)
    best_solution, stats = engine.run()
    engine.save_stats_to_file(stats)
    print(best_solution, sep="")


if __name__ == "__main__":
    main()
