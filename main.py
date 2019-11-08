from genetic import run, save_population_to_file, save_statistics_to_file
from graph import UI
from grids import *
from sudoku import Sudoku


def main():
    given_cells = impossible_521901
    output = run(individual_class=Sudoku, population_size=1000, log=True, display_best=False, given_cells=given_cells)
    file_pop_path = save_population_to_file(output["population_history"])
    save_statistics_to_file(output["statistics"])

    # Report
    print(f"generation number: {output['generation_count']}")
    print("Best solution of last population:")
    print(sorted(output["population_history"][-1], key=lambda i: i.normalized_rate())[-1])

    # Graph
    config = {'populations_save': file_pop_path, 'statics': ''}
    ui = UI('Sodoku', config)
    ui.show()


if __name__ == "__main__":
    main()
