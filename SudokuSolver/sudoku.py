from random import random, shuffle, choice, randint
from time import time
from typing import Tuple, Optional, Set, List, Union

from SudokuSolver.genetic import Individual, Number


class Position:
    """Holds the coordinates of a Cell"""
    def __init__(self, coordinates: Tuple[int, int]):
        self.coordinates = coordinates

    def __repr__(self):
        return f"{self.coordinates[0]}, {self.coordinates[1]}"


class Cell:
    """
    Represents a cell of a sudoku board
    """
    def __init__(self, position: Position, value: Optional[int]):
        self.position = position
        self.value = value

    @staticmethod
    def build(*data: Tuple[int, int, int]) -> Set["Cell"]:
        """
        Utils method used to build a Sudoku board from a Tuple of pre-filled cells (the initial grid)
        """
        return {Cell(Position((x, y)), value) for x, y, value in data}

    def __repr__(self):
        """Display self in a dev friendly way"""
        return f"{type(self).__name__}({self.position}, value={self.value})"

    def copy(self) -> "Cell":
        return Cell(self.position, self.value)


class Sudoku(Individual):
    """
    Represent a potential sudoku solution
    """
    # Probability of having a mutation on a gene
    # 1 means all genes will be mutated
    mutation_probability = 0.03
    # mutation_probability = 0.003
    mating_probability = 0.5

    # noinspection PyMissingConstructor
    def __init__(self, given_cells: Set[Cell]):
        self.width = 6  # The size of the grid
        self.height = self.width
        self.square_width = 3  # The width of a square
        self.square_height = 2  # Its height
        self.value_number = max(self.width, self.height)  # The number of potential values for a cell (9 for a 9x9 grid)
        # Check the coherence of the grid parameters
        assert self.width % self.square_width == 0
        assert self.height % self.square_height == 0
        assert self.square_width * self.square_height == self.width

        # These two variables are the minimum and maximum output of the _rate mathod
        self.floor = (  # It is the minimum possible score
            (1 * self.width) ** 2
            + (1 * self.height) ** 2
            + (1 * self.square_width * self.square_height) ** 2
            + (0 * self.value_number) ** 2
        )
        self.maxi = (  # The maximum possible score
            (self.value_number * self.width) ** 2
            + (self.value_number * self.height) ** 2
            + (self.value_number * self.square_width * self.square_height) ** 2
            + (1 * self.value_number) ** 2
        )

        self.given_cells = given_cells  # The cells given at the beginning

        # The solution proposed by self. For now it contains only the given cells
        self.cells: Set[Cell] = given_cells.copy()

        # Build the unknown cells and fill them with None by default
        coordinates = set()
        for given_cell in given_cells:
            coordinates.add(given_cell.position.coordinates)
            assert 0 <= given_cell.position.coordinates[0] < self.width
            assert 0 <= given_cell.position.coordinates[1] < self.height
        for i in range(self.width):
            for j in range(self.height):
                if (i, j) not in coordinates:
                    self.cells.add(Cell(Position((i, j)), None))

        assert len(self.cells) == self.width * self.height

        # Randomly fill the unknown cells
        self.randomly_fill()

    def build_random_valid_sudoku_values(self, given_values: List[int]) -> List[int]:
        """Returns the list of the missing values to validly fill self"""
        numbers = []
        max_value = max(self.width, self.height)
        min_value = min(self.width, self.height)
        for _ in range(min_value):
            for i in range(1, max_value + 1):
                if i in given_values:
                    given_values.remove(i)
                else:
                    numbers.append(i)
        return numbers

    def clone(self) -> "Individual":
        new = Sudoku(self.given_cells)
        # Replace the randomly filled cells by its parent ones
        # We should probably optimize this by preventing to randomly fill while cloning
        new.cells = {cell.copy() for cell in self.cells}
        new.mutation_probability = self.mutation_probability
        new.mating_probability = self.mating_probability
        return new

    def mate(self, other: "Sudoku") -> "Individual":
        """This method combine two grids by cutting them in two parts and merging one part of each parent"""
        new = Sudoku(self.given_cells)

        # Choose mutation and mating probability from one parent at random
        new.mutation_probability = choice((self.mutation_probability, other.mutation_probability))
        new.mating_probability = choice((self.mating_probability, other.mating_probability))

        # 0 means split in the rows, 1 means split in the columns
        crossover_type = choice([0, 1])
        index_where_to_split = randint(0, self.width - 2) if crossover_type == 1 else randint(0, self.height - 2)
        new.cells = {
            (f_cell.copy() if f_cell.position.coordinates[crossover_type] < index_where_to_split else m_cell.copy())
            for f_cell, m_cell in zip(self.cells, other.cells)
        }
        return new

    def randomly_fill(self):
        """Fill self with random values"""
        values = self.build_random_valid_sudoku_values([i.value for i in self.given_cells])
        shuffle(values)
        for cell, value in zip(self.cells.difference(self.given_cells), values):
            cell.value = value

    def _rate(self) -> Number:
        """
        Returns the score of self.
        Here is how it is computed :
        For each row add the number of different numbers it contains. For example this row : 1, 2, 5, 4, 2 is worth 4
        Same for each column and for each square.
        Add 1 if a number is n times in the grid where n is the number of time it should appear.
        For example in a 9x9 grid if the number 4 appears 9 time the score will be incremented by 1
        Add 0.5 if a number is n-1 times in the grid and 0.25 for n-2
        Each factor is modified by an arbitrary operation.
        Actually, it **2 for each but if you want to increase or decrease the importance of one of them,
        feel free to modify these operations.
        For example, if you want to increase the importance of having correct columns, you may apply **3 to it.
        """
        rows, columns, squares = {}, {}, {}
        values_count = {}
        for cell in self.cells:
            row_key = cell.position.coordinates[0]
            column_key = cell.position.coordinates[1]
            square_key = (
                cell.position.coordinates[0] // self.square_width,
                cell.position.coordinates[1] // self.square_height,
            )
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
            sum([len(it) for it in rows.values()]) ** 2
            + sum([len(it) for it in columns.values()]) ** 2
            + sum([len(it) for it in squares.values()]) ** 2
            + sum(
                [
                    {self.value_number: 1, self.value_number - 1: 0.5, self.value_number - 2: 0.25}.get(value, 0)
                    for value in values_count.values()
                ]
            )
            ** 2
        )

    def mutate(self):
        """
        Apply a random mutation on randomly chosen cells open to modification
        """
        for cell_to_mutate in self.cells - self.given_cells:
            if random() < self.mutation_probability:
                assert cell_to_mutate not in self.given_cells
                cell_to_mutate.value = randint(1, self.value_number)
        # Un-comment this snippet if you want to allow mutation on mutation and mating probability
        # if random() < self.mutation_probability:
        #     self.mutation_probability = random()
        #     self.mutation_probability *= choice([0.99, 1.01])
        # if random() < self.mutation_probability:
        #     self.mating_probability = random()

    def __str__(self):
        """
        This method is able to build an ascii art sudoku grid of arbitrary column, row and square size
        Numbers are represented as letter. Upper meaning given initial number
        """
        letters = {i + 1: letter for i, letter in enumerate("abcdefghijklmnopqrstuvwxyz")}
        letters[None] = "-"
        cells: List[List[Union[int, str]]] = [[0 for __ in range(self.width)] for _ in range(self.height)]
        for cell in self.cells - self.given_cells:
            cells[cell.position.coordinates[1]][cell.position.coordinates[0]] = letters[cell.value]
        for given_cell in self.given_cells:
            cells[given_cell.position.coordinates[1]][given_cell.position.coordinates[0]] = letters[
                given_cell.value
            ].upper()
        for row in cells:
            for i in range(self.width // self.square_width + 1):
                row.insert(self.square_width * i + i, "|")
        cells: List[Union[int, str]] = [" ".join([str(cell) for cell in row]) for row in cells]
        for i in range(self.height // self.square_height + 1):
            cells.insert(self.square_height * i + i, "-" * (1 + self.width * 2 + (self.width // self.square_width) * 2))
        return "\n".join(cells)


if __name__ == "__main__":
    start = time()
    grid = Sudoku({Cell(Position((3, 5)), 8)})
    grid.randomly_fill()
    print(grid.normalized_rate())
    print("\n".join([str(it) for it in grid.cells]))
