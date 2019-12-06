import os
import pickle
from datetime import datetime
from random import choices, random
from typing import Type, List, Optional, Union, Tuple

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


class StatCollector:
    total_sum = 0
    values_number = 0
    greatest = None
    greatest_item = None
    greatest_id = None
    smallest = None
    smallest_item = None

    def collect(self, value: Number, item: Individual, uid):
        self.total_sum += value
        if self.greatest is None or value > self.greatest:
            self.greatest = value
            self.greatest_item = item
            self.greatest_id = uid
        if self.smallest is None or value < self.smallest:
            self.smallest = value
            self.smallest_item = item
        self.values_number += 1

    @property
    def mean(self):
        return self.total_sum / self.values_number


def init_population(individual_type: Type[Individual], pop_size: int, *args, **kwargs) -> Population:
    # noinspection PyArgumentList
    return [individual_type(*args, **kwargs) for _ in range(pop_size)]


class ExitReasons:
    KEYBOARD_INTERRUPT = 0
    SUCCESS = 1
    BLOCKED = 2


class GeneticEngine:
    def __init__(
        self, individual_class: Type[Individual], population_size, *individual_init_args, **individual_init_kwargs
    ):

        self.INDIVIDUAL_CLASS = individual_class
        self.POPULATION_SIZE = population_size
        self.INDIVIDUAL_INIT_ARGS = individual_init_args
        self.INDIVIDUAL_INIT_KWARGS = individual_init_kwargs

    def init_population(self) -> Population:
        # noinspection PyArgumentList
        return [
            self.INDIVIDUAL_CLASS(*self.INDIVIDUAL_INIT_ARGS, **self.INDIVIDUAL_INIT_KWARGS)
            for _ in range(self.POPULATION_SIZE)
        ]

    def run_generation(self, population: Population, do_not_mutate: Optional[Individual]):

        score_stats = StatCollector()
        mutation_probability_stats = StatCollector()
        mating_probability_stats = StatCollector()

        scores = []
        for index, individual in enumerate(population):

            if individual is not do_not_mutate:
                individual.mutate()

            score = individual.normalized_rate()
            scores.append(score)

            score_stats.collect(score, individual, index)
            mutation_probability_stats.collect(individual.mutation_probability, individual, index)
            mating_probability_stats.collect(individual.mating_probability, individual, index)

        biased_scores = [score ** 10 for score in scores]
        for i, (father, mother) in enumerate(
            zip(
                choices(population, biased_scores, k=self.POPULATION_SIZE - 1),
                choices(population, biased_scores, k=self.POPULATION_SIZE - 1),
            )
        ):
            population[i] = father.reproduce(mother)

        if do_not_mutate is not None:
            population.append(do_not_mutate)

        return score_stats, mutation_probability_stats, mating_probability_stats

    def run_population(self):
        population = self.init_population()

        population_score_stats = []
        population_best_individuals = []

        best_individual = None
        all_time_best_score = None

        no_progress_count = 0
        generation_count = 0

        keep_running = True
        while keep_running:

            try:
                score_stats, mutation_probability_stats, mating_probability_stats = self.run_generation(
                    population, do_not_mutate=best_individual
                )
                best_individual = score_stats.greatest_item

                text = (
                    f"{format(score_stats.greatest, '<4.2f')}\t"
                    f"{format(score_stats.mean, '<4.2f')}\t"
                    f"{format(score_stats.smallest, '<4.2f')}\t"
                    f"{format(mutation_probability_stats.mean, '<4.4f')}\t"
                    f"{format(mating_probability_stats.mean, '<4.4f')}\t"
                    f"{generation_count}"
                )
                print(f"\r{text}", end="")

                population_score_stats.append((score_stats.greatest, score_stats.mean, score_stats.smallest,
                                               score_stats.greatest_id))
                population_best_individuals.append(best_individual)

                if all_time_best_score is None or score_stats.greatest > all_time_best_score:
                    all_time_best_score = score_stats.greatest
                    no_progress_count = 0
                    if all_time_best_score >= 100:
                        keep_running = False
                        exit_reason = ExitReasons.SUCCESS

                else:
                    no_progress_count += 1
                    if generation_count > 20 and no_progress_count == generation_count // 2:
                        keep_running = False
                        exit_reason = ExitReasons.BLOCKED

                generation_count += 1

            except KeyboardInterrupt:
                keep_running = False
                exit_reason = ExitReasons.KEYBOARD_INTERRUPT

        # noinspection PyUnboundLocalVariable
        return population_best_individuals, population_score_stats, exit_reason

    def run(self):
        print("max ", "avg ", "min ", "mut-pr", "mat-pr", "g-nbr", sep="\t")
        keep_running = True
        best_individuals = []
        population_stats = []

        while keep_running:
            best_individuals, population_stats, exit_reason = self.run_population()
            if exit_reason != ExitReasons.BLOCKED:
                keep_running = False
        print("\n", end="")

        return best_individuals, population_stats

    def save_stats_to_file(self, data: List[List[Tuple[Number, Number, Number]]], export_type: str) -> str:
        directory_name = "data"

        # Check that the data directory is free
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        elif not os.path.isdir(directory_name):
            raise RuntimeError("./data is not a directory")

        # Compute a nice file name
        file_path = os.path.join(
            directory_name, f"{export_type}_{self.INDIVIDUAL_CLASS.__name__.lower()}_{datetime.now()}".replace(" ", "_")
        )

        with open(file_path, "wb") as f:
            pickle.dump(data, f)

        # Source : https://stackoverflow.com/a/32009595/7629797
        suffixes = ["B", "KB", "MB", "GB", "TB"]
        suffix_index = 0
        size = os.path.getsize(file_path)
        while size > 1024 and suffix_index < 4:
            suffix_index += 1  # increment the index of the suffix
            size = size / 1024.0  # apply the division
        human_readable_size = "%.*f%s" % (2, size, suffixes[suffix_index])

        print(f"population saved into {os.path.abspath(file_path)}" f" File size : {human_readable_size}")

        return os.path.abspath(file_path)
