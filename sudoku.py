from random import random, shuffle, choices
from time import time
from typing import Tuple, Optional, Set, List

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


class Grid(Individual):
    def clone(self) -> "Individual":
        new = Grid(self.given_cells)
        new.cells = {cell.copy() for cell in self.cells}
        return new

    def mate(self, other: "Individual") -> "Individual":
        return self.clone()

    def __init__(self, given_cells: Set[Cell]):
        self.mutation_probability = 0.1
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
        # print(self)
        # exit()

    def randomly_fill(self):
        values = build_random_valid_sudoku_values([i.value for i in self.given_cells])
        shuffle(values)
        for cell, value in zip(self.cells.difference(self.given_cells), values):
            cell.value = value

    def _rate(self) -> Number:
        rows, columns, squares = {}, {}, {}
        for cell in self.cells:
            row_key = cell.position.coordinates[0]
            column_key = cell.position.coordinates[1]
            square_key = (cell.position.coordinates[0] % 3, cell.position.coordinates[1] % 3)
            if row_key not in rows:
                rows[row_key] = set()
            rows[row_key].add(cell.value)
            if column_key not in columns:
                columns[column_key] = set()
            columns[column_key].add(cell.value)
            if square_key not in squares:
                squares[square_key] = set()
            squares[square_key].add(cell.value)
        return (
            sum([len(it) for it in rows.values()])
            + sum([len(it) for it in columns.values()])
            + sum([len(it) for it in squares.values()])
        )

    def mutate(self):
        if random() < self.mutation_probability:
            cells = list(self.cells.difference(self.given_cells))
            cell1, cell2 = choices(cells, k=2)
            cell1.value, cell2.value = cell2.value, cell1.value

    def __repr__(self):
        cells = [[0 for __ in range(9)] for _ in range(9)]
        for cell in self.cells:
            cells[cell.position.coordinates[1]][cell.position.coordinates[0]] = cell.value
        cells = [" ".join([str(cell) for cell in row]) for row in cells]
        return "\n".join(cells)


if __name__ == "__main__":
    start = time()
    grid = Grid({Cell(Position((3, 5)), 8)})
    grid.randomly_fill()
    print(grid.normalized_rate())
    print("\n".join([str(it) for it in grid.cells]))
