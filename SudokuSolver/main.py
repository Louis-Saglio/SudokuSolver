from time import time

from SudokuSolver.genetic import GeneticEngine
from SudokuSolver.grids import *
from SudokuSolver.sudoku import Sudoku


def with_gui_report():
    from SudokuSolver.graphic_interface import UI
    given_cells = small_6x6_112
    engine = GeneticEngine(individual_class=Sudoku, population_size=1000, given_cells=given_cells)
    best_solutions, stats = engine.run()
    stats_file = engine.save_stats_to_file(stats, 'stats')
    population_file = engine.save_stats_to_file(best_solutions, 'population')

    config = {'statistics': stats_file, 'given_cells': given_cells, 'populations_save': population_file}
    ui = UI('Sodoku solver', config)
    ui.show()

    print(best_solutions[0], sep="")


def pure_cmd():
    start = time()
    engine = GeneticEngine(individual_class=Sudoku, population_size=1000, given_cells=small_6x6_112)
    best_solutions, stats = engine.run()
    print(round(time() - start, 2), "seconds")
    # engine.save_stats_to_file(stats)
    print(best_solutions[-1], sep="")


if __name__ == '__main__':
    pure_cmd()
    # with_gui_report()
