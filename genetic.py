from random import choices
from statistics import mean
from typing import Type, List, Iterable


class Individual:
    mutation_rate: float = 0.1

    def rate(self) -> int:
        raise NotImplementedError

    def mutate(self):
        raise NotImplementedError

    def clone(self) -> "Individual":
        raise NotImplementedError

    def mate(self, other: "Individual") -> "Individual":
        raise NotImplementedError

    def reproduce(self, other: "Individual") -> "Individual":
        if other is self:
            return self.clone()
        return self.mate(other)


Population = List[Individual]


def init_population(individual_type: Type[Individual], pop_size: int, *args, **kwargs) -> Population:
    # noinspection PyArgumentList
    return [individual_type(*args, **kwargs) for _ in range(pop_size)]


def mutate(population: Iterable[Individual]):
    for individual in population:
        individual.mutate()


def reproduce(population: Population) -> Population:
    scores = [max(i.rate(), 1) ** 2 for i in population]
    new_pop_f = choices(population, scores, k=len(population))
    new_pop_m = choices(population, scores, k=len(population))
    return [father.reproduce(mother) for father, mother in zip(new_pop_f, new_pop_m)]


def run(individual_class: Type[Individual], population_size, *args, **kwargs):
    population = init_population(individual_class, population_size, *args, **kwargs)
    while True:
        try:
            mutate(population)
            population = reproduce(population)
            scores = [i.rate() for i in population]
            print("-" * 30)
            print(min(scores))
            print(mean(scores))
            print(max(scores))
            pass
        except KeyboardInterrupt:
            break
    print(sorted(population, key=lambda i: i.rate()))
