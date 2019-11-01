from random import randint, random
from time import time
from typing import Tuple, Optional, Set

from genetic import Individual


class Position:
    def __init__(self, coordinates: Tuple[int, int]):
        self.coordinates = coordinates

    def __repr__(self):
        return f"{self.coordinates[0]}, {self.coordinates[1]}"


class Cell:
    def __init__(self, position: Position, value: Optional[int]):
        self.position = position
        self.value = value

    def __repr__(self):
        return f"{type(self).__name__}({self.position}, value={self.value})"

    def copy(self) -> "Cell":
        return Cell(self.position, self.value)


class Grid(Individual):
    def clone(self) -> "Individual":
        new = Grid(self.given_cells)
        new.cells = [cell.copy() for cell in self.cells]
        return new

    def mate(self, other: "Individual") -> "Individual":
        return self.clone()

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
        for cell in self.cells:
            if cell not in self.given_cells:
                cell.value = randint(1, 9)

    def rate(self) -> int:
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
        for cell in self.cells:
            if random() < self.mutation_probability:
                cell.value = randint(1, 9)

    def __repr__(self):
        cells = [[0 for __ in range(9)] for _ in range(9)]
        for cell in self.cells:
            cells[cell.position.coordinates[0]][cell.position.coordinates[1]] = cell.value
        cells = [" ".join([str(cell) for cell in row]) for row in cells]
        return "\n".join(cells)


if __name__ == "__main__":
    start = time()
    grid = Grid({Cell(Position((3, 5)), 8)})
    grid.randomly_fill()
    print(grid.rate())
    print("\n".join([str(it) for it in grid.cells]))
