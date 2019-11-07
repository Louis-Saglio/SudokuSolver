import os
import pickle
from datetime import datetime
from multiprocessing import Queue
from random import choices, random
from statistics import mean
from time import time
from typing import Type, List, Optional, Union

Number = Union[float, int]


class Individual:
    mutation_probability: float = 1
    mating_probability: float = 1
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


def run(individual_class: Type[Individual], population_size, log: bool = False, *args, **kwargs):
    population = init_population(individual_class, population_size, *args, **kwargs)
    population_history = [population]

    if log:
        print("max ", "avg ", "min ", "mut-pr", "mat-pr", "g-nbr", sep="\t")

    generation_count = 0
    keep_running = True
    start = time()
    while keep_running:
        try:
            scores = []
            for individual in population:
                individual.mutate()

                score = individual.normalized_rate()
                scores.append(score)

                if score == 100:
                    keep_running = False

            # Reproduce
            biased_scores = [score ** 10 for score in scores]
            new_pop_f = choices(population, biased_scores, k=population_size)
            new_pop_m = choices(population, biased_scores, k=population_size)
            population = [father.reproduce(mother) for father, mother in zip(new_pop_f, new_pop_m)]

            if log:
                maxi, avg, mini, mean_mut_prob, mean_mat_prob = (
                    max(scores),
                    mean(scores),
                    min(scores),
                    mean([i.mutation_probability for i in population]),
                    mean([i.mating_probability for i in population]),
                )
                print(
                    f"\r{format(maxi, '<4.2f')}\t"
                    f"{format(avg, '<4.2f')}\t"
                    f"{format(mini, '<4.2f')}\t"
                    f"{format(mean_mut_prob, '<4.4f')}\t"
                    f"{format(mean_mat_prob, '<4.4f')}\t"
                    f"{generation_count}",
                    end="",
                )

        except KeyboardInterrupt:
            keep_running = False

        generation_count += 1

        # todo : un comment the following line to enable saving all population history to disk.
        #  unfortunately, this functionality quickly eat all the RAM and need to be re-thought
        # population_history.append(population)

    population_history.append(population)  # For now, only add the latest generation to history

    if log:
        time_per_generation = (time() - start) * 1000 / generation_count
        print(f"\n{round(time_per_generation, 2)} ms / generation")
        print(f"{round(time_per_generation / population_size, 2)} ms / individual")

    return {"population_history": population_history, "generation_count": generation_count}


def train_population(population: Population, queue: Queue, stop_when_no_improvements_during: int = 1000):
    pass


def save_population_to_file(populations: List[Population], file_path: Optional[str] = None) -> None:
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


def human_readable_size(size, precision=2):
    # Source : https://stackoverflow.com/a/32009595/7629797
    suffixes = ["B", "KB", "MB", "GB", "TB"]
    suffix_index = 0
    while size > 1024 and suffix_index < 4:
        suffix_index += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffix_index])
