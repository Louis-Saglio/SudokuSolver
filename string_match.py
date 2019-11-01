from random import random, randint, choice
from string import ascii_lowercase

from genetic import Individual, Number


class String(Individual):
    goal = "loremipsumdolorsitamet"

    def __init__(self, name):
        self.name = name
        self.maxi = 22
        self.floor = 0

    def mutate(self):
        if random() < 0.1:
            self.name = "".join(
                [
                    (choice(ascii_lowercase) if i == randint(0, len(self.name) - 1) else l)
                    for i, l in enumerate(self.name)
                ]
            )

    def _rate(self) -> Number:
        return sum([1 for l, o in zip(self.name, self.goal) if l == o])

    def __repr__(self):
        return f"{''.join([(l.upper() if l == o else l) for l, o in zip(self.name, self.goal)])} -> {self._rate()}"

    def clone(self) -> "Individual":
        return String(self.name)

    def mate(self, other: "String") -> "Individual":
        name = self.name[0 : randint(0, len(self.name))] + other.name[randint(0, len(other.name)) : len(other.name)]
        return String(name[:22])
