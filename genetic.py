import pickle
from datetime import datetime
from random import choices, random
from statistics import mean
from time import time
from typing import Type, List, Iterable, Optional, Callable, Union
import os


Number = Union[float, int]


class Individual:
    mutation_probability: float = 0.001
    mating_probability: float = 0.01
    floor: Number
    maxi: Number

    def _rate(self) -> Number:
        raise NotImplementedError

    def normalized_rate(self) -> Number:
        try:
            floor = self.floor
        except AttributeError:
            raise NotImplementedError(f"{type(self).__name__} must implement abstract floor attribute")
        try:
            maxi = self.maxi
        except AttributeError:
            raise NotImplementedError(f"{type(self).__name__} must implement abstract maxi attribute")
        return (self._rate() - floor) * 100 / (maxi - floor)

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
    scores = [max(i.normalized_rate(), 1) ** 10 for i in population]
    new_pop_f = choices(population, scores, k=len(population))
    new_pop_m = choices(population, scores, k=len(population))
    return [father.reproduce(mother) for father, mother in zip(new_pop_f, new_pop_m)]


def run(individual_class: Type[Individual], population_size, log_state: bool = False, *args, **kwargs):
    population = init_population(individual_class, population_size, *args, **kwargs)
    population_history = [population]

    if log_state:
        print("max ", "avg ", "min ", "g-nbr", sep="\t")

    generation_count = 0
    keep_running = True
    start = time()
    while keep_running:
        try:
            mutate(population)
            population = reproduce(population)

            scores = []
            for individual in population:
                score = individual.normalized_rate()
                scores.append(score)
                if score == 100:
                    keep_running = False

            if log_state:
                maxi, avg, mini = max(scores), mean(scores), min(scores)
                print(
                    f"\r{format(maxi, '<4.2f')}\t{format(avg, '<4.2f')}\t{format(mini, '<4.2f')}\t{generation_count}",
                    end="",
                )

        except KeyboardInterrupt:
            keep_running = False

        generation_count += 1

        # todo : un comment the following line to enable saving all population history to disk.
        #  unfortunately, this functionality quickly eat all the RAM and need to be re-thought
        # population_history.append(population)

    population_history.append(population)  # For now, only add the latest generation to history

    if log_state:
        time_per_generation = (time() - start) * 1000 / generation_count
        print(f"\n{round(time_per_generation, 2)} ms / generation")
        print(f"{round(time_per_generation / population_size, 2)} ms / individual")

    return {"population_history": population_history, "generation_count": generation_count}


def save_population_to_file(populations: List[Population], file_path: Optional[str] = None) -> str:
    if file_path is None:
        directory_name = "data"

        # Check that the data directory is free
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        elif not os.path.isdir(directory_name):
            raise RuntimeError("./data is not a directory")

        # Compute a nice file name
        file_path = os.path.join(
            directory_name,
            f"{type(populations[0]).__name__.lower()}"
            f"_{mean([i.normalized_rate() for i in populations[-1]])}_{datetime.now()}".replace(" ", "_"),
        )

    with open(file_path, "wb") as f:
        pickle.dump(populations, f)

    print(
        f"population saved into {os.path.abspath(file_path)}"
        f" File size : {human_readable_size(os.path.getsize(file_path))}"
    )
    return file_path


def human_readable_size(size, precision=2):
    # Source : https://stackoverflow.com/a/32009595/7629797
    suffixes = ["B", "KB", "MB", "GB", "TB"]
    suffix_index = 0
    while size > 1024 and suffix_index < 4:
        suffix_index += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffix_index])
