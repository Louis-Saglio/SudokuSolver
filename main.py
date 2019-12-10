from genetic import GeneticEngine
from graphic_interface import UI
from grids import *
from sudoku import Sudoku


def main():
    given_cells = small_6x6_112
    engine = GeneticEngine(individual_class=Sudoku, population_size=1000, given_cells=given_cells)
    best_solutions, stats = engine.run()
    stats_file = engine.save_stats_to_file(stats, 'stats')
    population_file = engine.save_stats_to_file(best_solutions, 'population')

    config = {'statistics': stats_file, 'given_cells': given_cells, 'populations_save': population_file}
    ui = UI('Sodoku solver', config)
    ui.show()

    print(best_solutions[-1], sep="")


if __name__ == "__main__":
    main()
