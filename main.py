from genetic import run, save_population_to_file, save_statistics_to_file
from grids import *
from sudoku import Sudoku


def main():
    given_cells = empty
    output = run(individual_class=Sudoku, population_size=50, log=True, display_best=False, given_cells=given_cells)
    save_population_to_file(output["population_history"])
    save_statistics_to_file(output["statistics"])

    # Report
    print(f"generation number: {output['generation_count']}")
    print("Best solution of last population:")
    print(sorted(output["population_history"][-1], key=lambda i: i.normalized_rate())[-1])


if __name__ == "__main__":
    main()
