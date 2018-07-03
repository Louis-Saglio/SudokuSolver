import random


class Grid:

    def __init__(self, dimensions=(9, 9), pre_filled_nbr=0):
        self.dimensions = dimensions
        self.cells = {}
        for position in self._get_random_positions(pre_filled_nbr):
            self.cells[position] = 0

    def _get_random_positions(self, nbr):
        # todo : max nbr **3
        # todo : forbid doubles
        return tuple(zip(*[random.choices(range(dim_size), k=nbr) for dim_size in self.dimensions]))

    def __repr__(self):
        if len(self.dimensions) != 2:
            return f"{self.__class__.__name__}{{dimensions={self.dimensions}, cells={self.cells}}}"
        rep = []
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                rep.append(f"{self.cells.get((x, y), ' ')} ")
            rep.append('\n')
        return ''.join(rep)


def main():
    grid = Grid(pre_filled_nbr=30)
    print(grid)


if __name__ == '__main__':
    main()
