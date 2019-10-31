import pickle
from datetime import datetime
from random import choices, random
from statistics import mean
from typing import Type, List, Iterable, Optional, Callable, Union
import os


class Individual:
    mutation_probability: float = 0.01
    mating_probability: float = 0.01

    def rate(self) -> int:
        raise NotImplementedError

    def mutate(self):
        raise NotImplementedError

    def clone(self) -> "Individual":
        raise NotImplementedError

    def mate(self, other: "Individual") -> "Individual":
        raise NotImplementedError

    def reproduce(self, other: "Individual") -> "Individual":
        if other is self or random() > self.mating_probability:
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


Number = Union[float, int]


def run(
    individual_class: Type[Individual],
    population_size,
    stop_condition: Callable[[Population, Number, Number, Number], bool],
    *args,
    **kwargs,
):
    populations = []
    population = init_population(individual_class, population_size, *args, **kwargs)
    populations.append(population)
    print("max ", "avg ", "min ", sep="\t")
    while True:
        try:
            mutate(population)
            population = reproduce(population)
            scores = [i.rate() for i in population]
            maxi, avg, mini = max(scores), mean(scores), min(scores)
            print(f"\r{format(maxi, '<4')}\t{format(avg, '<4')}\t{format(mini, '<4')}", end="")
            if stop_condition(population, mini, avg, maxi):
                break
        except KeyboardInterrupt:
            break
        populations.append(population)
    print()
    print(sorted(population, key=lambda i: i.rate()))
    return populations


def save_population_to_file(populations: List[Population], file_path: Optional[str] = None) -> None:
    if file_path is None:
        directory_name = "data"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        elif not os.path.isdir(directory_name):
            raise RuntimeError("./data is not a directory")
        file_path = os.path.join(directory_name, f"saved_population_history_{datetime.now()}")
    with open(file_path, "wb") as f:
        pickle.dump(populations, f)
    print(
        f"population saved into {os.path.abspath(file_path)}"
        f" File size : {human_readable_size(os.path.getsize(file_path))}"
    )


def human_readable_size(size, precision=2):
    # Source : https://stackoverflow.com/a/32009595/7629797
    suffixes = ["B", "KB", "MB", "GB", "TB"]
    suffix_index = 0
    while size > 1024 and suffix_index < 4:
        suffix_index += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffix_index])
