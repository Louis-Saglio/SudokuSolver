from genetic import run, save_population_to_file
from sudoku import Grid, Cell


def main():
    given_cells = Cell.build(
        (1, 0, 2),
        (3, 0, 1),
        (5, 0, 5),
        (8, 0, 6),
        (0, 1, 1),
        (4, 1, 9),
        (5, 1, 2),
        (6, 1, 8),
        (7, 1, 5),
        (0, 2, 3),
        (2, 2, 5),
        (4, 2, 8),
        (2, 3, 7),
        (3, 3, 8),
        (6, 3, 5),
        (8, 3, 2),
        (0, 4, 4),
        (4, 4, 2),
        (8, 4, 9),
        (0, 5, 6),
        (2, 5, 2),
        (5, 5, 3),
        (6, 5, 4),
        (4, 6, 1),
        (6, 6, 7),
        (8, 6, 3),
        (1, 7, 8),
        (2, 7, 3),
        (3, 7, 6),
        (4, 7, 4),
        (8, 7, 5),
        (0, 8, 2),
        (3, 8, 5),
        (5, 8, 7),
        (7, 8, 8),
    )
    population = run(Grid, 1000, lambda *args: False, given_cells=given_cells)[0]
    save_population_to_file(population)
    print("Best solution :")
    print(sorted(population, key=lambda i: i.normalized_rate())[-1])


if __name__ == "__main__":
    main()
