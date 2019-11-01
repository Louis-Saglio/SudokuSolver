from genetic import run, save_population_to_file
from sudoku import Grid


def main():
    population = run(Grid, 1000, lambda *args: False, given_cells=set())[0]
    save_population_to_file(population)
    print("Best solution :")
    print(sorted(population, key=lambda i: i.rate())[-1])


if __name__ == "__main__":
    main()
