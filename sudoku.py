from random import random, shuffle, choices, choice, randint
from time import time
from typing import Tuple, Optional, Set, List, Union

from genetic import Individual, Number


def build_random_valid_sudoku_values(given_values: List[int]) -> List[int]:
    numbers = []
    for _ in range(9):
        for i in range(1, 10):
            if i in given_values:
                given_values.remove(i)
            else:
                numbers.append(i)
    return numbers


class Position:
    def __init__(self, coordinates: Tuple[int, int]):
        self.coordinates = coordinates

    def __repr__(self):
        return f"{self.coordinates[0]}, {self.coordinates[1]}"


class Cell:
    def __init__(self, position: Position, value: Optional[int]):
        self.position = position
        self.value = value

    @staticmethod
    def build(*data: Tuple[int, int, int]) -> Set["Cell"]:
        return {Cell(Position((x, y)), value) for x, y, value in data}

    def __repr__(self):
        return f"{type(self).__name__}({self.position}, value={self.value})"

    def copy(self) -> "Cell":
        return Cell(self.position, self.value)

    def __hash__(self):
        return hash(self.position.coordinates)

    def __eq__(self, other):
        return hash(self) == hash(other)


class Sudoku(Individual):
    mutation_probability = 0.001
    mating_probability = 1
    floor = (9 * 1) + (9 * 1) + (9 * 1) + (9 * 0)
    maxi = (9 * 9) + (9 * 9) + (9 * 9) + (9 * 1)

    def clone(self) -> "Individual":
        new = Sudoku(self.given_cells)
        new.cells = {cell.copy() for cell in self.cells}
        new.mutation_probability = self.mutation_probability
        new.mating_probability = self.mating_probability
        return new

    def mate(self, other: "Sudoku") -> "Individual":
        crossover_type = choice([0, 1])
        index_where_to_split = randint(0, 7)
        new = Sudoku(self.given_cells)
        new.mutation_probability = choice((self.mutation_probability, other.mutation_probability))
        new.mating_probability = choice((self.mating_probability, other.mating_probability))
        new.cells = {
            (f_cell.copy() if f_cell.position.coordinates[crossover_type] < index_where_to_split else m_cell.copy())
            for f_cell, m_cell in zip(self.cells, other.cells)
        }
        return new

    def __init__(self, given_cells: Set[Cell]):
        self.given_cells = given_cells
        self.cells: Set[Cell] = given_cells.copy()
        self.dimensions = (9, 9)
        coordinates = {it.position.coordinates: it for it in self.given_cells}
        for i in range(self.dimensions[0]):
            for j in range(self.dimensions[1]):
                if (i, j) not in coordinates:
                    self.cells.add(Cell(Position((i, j)), None))
        assert len(self.cells) == 81
        self.randomly_fill()

    def randomly_fill(self):
        values = build_random_valid_sudoku_values([i.value for i in self.given_cells])
        shuffle(values)
        for cell, value in zip(self.cells.difference(self.given_cells), values):
            cell.value = value

    def _rate(self) -> Number:
        rows, columns, squares = {}, {}, {}
        values_count = {}
        for cell in self.cells:
            row_key = cell.position.coordinates[0]
            column_key = cell.position.coordinates[1]
            square_key = (cell.position.coordinates[0] % 3, cell.position.coordinates[1] % 3)
            value_key = cell.value
            if row_key not in rows:
                rows[row_key] = set()
            rows[row_key].add(cell.value)
            if column_key not in columns:
                columns[column_key] = set()
            columns[column_key].add(cell.value)
            if square_key not in squares:
                squares[square_key] = set()
            squares[square_key].add(cell.value)
            if value_key not in values_count:
                values_count[value_key] = 0
            values_count[value_key] += 1
        return (
            sum([len(it) for it in rows.values()])
            + sum([len(it) for it in columns.values()])
            + sum([len(it) for it in squares.values()])
            + sum([{9: 1, 8: 0.5, 7: 0.25}.get(value, 0) for value in values_count.values()])
        )

    def mutate(self):
        for cell_to_mutate in self.cells - self.given_cells:
            if random() < self.mutation_probability:
                assert cell_to_mutate not in self.given_cells
                cell_to_mutate.value = randint(1, 9)
        # if random() < self.mutation_probability:
        #     self.mutation_probability = random()
        #     self.mutation_probability *= choice([0.99, 1.01])
        # if random() < self.mutation_probability:
        #     self.mating_probability = random()

    def __str__(self):
        cells: List[List[Union[int, str]]] = [[0 for __ in range(9)] for _ in range(9)]
        for cell in self.cells:
            cells[cell.position.coordinates[1]][cell.position.coordinates[0]] = cell.value or "-"
        for row in cells:
            row.insert(0, "|")
            row.insert(4, "|")
            row.insert(8, "|")
            row.insert(12, "|")
        cells: List[Union[int, str]] = [" ".join([str(cell) for cell in row]) for row in cells]
        cells.insert(0, "-" * 25)
        cells.insert(4, "-" * 25)
        cells.insert(8, "-" * 25)
        cells.insert(12, "-" * 25)
        return "\n".join(cells)


if __name__ == "__main__":
    start = time()
    grid = Sudoku({Cell(Position((3, 5)), 8)})
    grid.randomly_fill()
    print(grid.normalized_rate())
    print("\n".join([str(it) for it in grid.cells]))
