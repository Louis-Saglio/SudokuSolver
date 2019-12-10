"""
This file contains the genetic algorithm engine
"""
import os
import pickle
from datetime import datetime
from random import choices, random
from typing import Type, List, Union, Tuple, Set

Number = Union[float, int]


class Individual:
    """
    This is the abstract class used to describe individuals.
    In order to solve a problem with this genetic algorithm engine,
    you must inherit from it and implements all the abstract methods to fit your particuliar problem
    """

    # This field is the probability of having a mutation
    # Usage of this field depends totally on the mutate method implementation
    mutation_probability: float = 1

    # This field is the probability of reproducing with a partner instead of cloning itself
    mating_probability: float = 1

    # This abstract field is the minimum score an individual can have.
    # it is used to standardize scores in the engine
    floor: Number

    # This is the maximum one
    maxi: Number

    def __init__(self, *args, **kwargs):
        pass

    def _rate(self) -> Number:
        """
        Returns the score of self. The bigger, the better
        """
        raise NotImplementedError

    def normalized_rate(self) -> Number:
        """
        This method is not supposed to be overriden.
        It normalizes the individual score between 0 and 100
        """
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
        """
        Describes how a mutation is supposed to modify the genome
        """
        raise NotImplementedError

    def clone(self) -> "Individual":
        """
        Returns a copy of itself.
        Do not include mutation.
        """
        raise NotImplementedError

    def mate(self, other: "Individual") -> "Individual":
        """
        Describes how an individual is supposed to reproduce with a partner (other).
        Do not include mutation.
        """
        raise NotImplementedError

    def reproduce(self, other: "Individual") -> "Individual":
        """
        Should not be overridden
        Reproduce with other or just clone itself according to mating_probability
        """
        if other is self or random() > self.mating_probability:
            return self.clone()
        return self.mate(other)


Population = List[Individual]


class StatCollector:
    """
    This is an utils class used to collect statistics during the engine runtime
    """

    total_sum: Number = 0
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


class ExitReasons:
    """
    Enum used to store the possible reasons why a population has stopped evolving.
    The engine may choose to do different actions according to these reasons
    """

    KEYBOARD_INTERRUPT = 0
    SUCCESS = 1
    BLOCKED = 2


class GeneticEngine:
    """
    This class contains all the logic of a genetic algorithm
    """

    def __init__(
        self, individual_class: Type[Individual], population_size, *individual_init_args, **individual_init_kwargs
    ):

        self.INDIVIDUAL_CLASS = individual_class
        self.POPULATION_SIZE = population_size
        self.INDIVIDUAL_INIT_ARGS = individual_init_args
        self.INDIVIDUAL_INIT_KWARGS = individual_init_kwargs

    def init_population(self) -> Population:
        """
        Instantiate a list of individual according to the arguments give to self.__init__
        """
        # noinspection PyArgumentList
        return [
            self.INDIVIDUAL_CLASS(*self.INDIVIDUAL_INIT_ARGS, **self.INDIVIDUAL_INIT_KWARGS)
            for _ in range(self.POPULATION_SIZE)
        ]

    def run_generation(self, population: Population, do_not_mutate: Set[Individual]):
        """
        Performs all the actions needed for a generation
        Collect statistics about this generation
        do_not_mutate is a set of individuals who should not be mutated.
        This feature is notably used to prevent mutation or sexual reproduction on the best individual
        """

        score_stats = StatCollector()
        mutation_probability_stats = StatCollector()
        mating_probability_stats = StatCollector()

        scores = []
        for index, individual in enumerate(population):
            assert individual is not None

            # Mutation
            if individual not in do_not_mutate:
                individual.mutate()

            score = individual.normalized_rate()
            scores.append(score)

            # Collect stats
            score_stats.collect(score, individual, index)
            mutation_probability_stats.collect(individual.mutation_probability, individual, index)
            mating_probability_stats.collect(individual.mating_probability, individual, index)

        # An individual with a score of 10 has 10 times more chances to reproduce
        # and have an offspring in the next generation
        # However this difference can be accentued by performing an arbitrary operation on the scores.
        # Empirical evidence showed that performing score ** 10 provided better results while trying to solve a sudoku.
        # Later version of this engine may provide a way of specifying this operation as a hyper-parameter
        # instead of hard-coding it
        biased_scores = [score ** 10 for score in scores]
        for i, (father, mother) in enumerate(
            zip(
                choices(population, biased_scores, k=self.POPULATION_SIZE - len(do_not_mutate)),
                choices(population, biased_scores, k=self.POPULATION_SIZE - len(do_not_mutate)),
            )
        ):
            population[i] = father.reproduce(mother)

        # In every case, add the individual not to mutate to the population
        population.extend(do_not_mutate)

        # Returns the collected stats
        return score_stats, mutation_probability_stats, mating_probability_stats

    def run_population(self):
        """
        Evolve a population until it succeeds or it is stuck in a local optimum
        Also collect stats about the population
        """
        population = self.init_population()

        # Variables used to collect statistics
        population_score_stats = []
        population_best_individuals = []
        best_individual = None
        all_time_best_score = None

        # These variables are used to detect if the population is stuck
        no_progress_count = 0
        generation_count = 0

        keep_running = True
        while keep_running:

            try:
                # Run one generation, do not mutate the best individual
                # Retrieve stats to later display them to the user
                score_stats, mutation_probability_stats, mating_probability_stats = self.run_generation(
                    population, do_not_mutate={best_individual} if best_individual else set()
                )
                best_individual = score_stats.greatest_item

                # Show to the user the advancement of the algorithm
                text = (
                    f"{format(score_stats.greatest, '<4.2f')}\t"
                    f"{format(score_stats.mean, '<4.2f')}\t"
                    f"{format(score_stats.smallest, '<4.2f')}\t"
                    f"{format(mutation_probability_stats.mean, '<4.4f')}\t"
                    f"{format(mating_probability_stats.mean, '<4.4f')}\t"
                    f"{generation_count}"
                )
                print(f"\r{text}", end="")

                # Collect stats and the individuals having the solution to the problem (best_individuals)
                population_score_stats.append(
                    (score_stats.greatest, score_stats.mean, score_stats.smallest, score_stats.greatest_id)
                )
                population_best_individuals.append(best_individual)

                # Check if we are stuck
                if all_time_best_score is None or score_stats.greatest > all_time_best_score:
                    # We just made progress
                    all_time_best_score = score_stats.greatest
                    no_progress_count = 0
                    if all_time_best_score >= 100:
                        # Check if we achieved the best score possible
                        # If yes, stop evolving
                        keep_running = False
                        exit_reason = ExitReasons.SUCCESS
                else:
                    # No progress has been made
                    no_progress_count += 1
                    if generation_count > 20 and no_progress_count >= generation_count // 2:
                        # If no progress has been made for half of the time,
                        # stop evolving since we are probably stuck in a local optimum
                        keep_running = False
                        exit_reason = ExitReasons.BLOCKED

                generation_count += 1

            except KeyboardInterrupt:
                # Gracefully handle ctrl+c
                keep_running = False
                exit_reason = ExitReasons.KEYBOARD_INTERRUPT

        # Returns solutions, stats and the reason why we stopped evolving
        # noinspection PyUnboundLocalVariable
        return population_best_individuals, population_score_stats, exit_reason

    def run(self):
        """
        Entry point of the genetic algorithm
        """
        # Display the headers to improve the readability of later logs
        print("max ", "avg ", "min ", "mut-pr", "mat-pr", "g-nbr", sep="\t")
        keep_running = True
        best_individuals = []
        population_stats = []

        while keep_running:
            # Evolve a population
            best_individuals, population_stats, exit_reason = self.run_population()
            if exit_reason != ExitReasons.BLOCKED:
                # If it stopped evolving and it is not blocked (either user exit or success), quit
                keep_running = False
            # Otherwise, build a new population and retry
        print("\n", end="")

        # Returns solutions and stats
        return best_individuals, population_stats

    def save_stats_to_file(self, data: List[List[Tuple[Number, Number, Number]]], export_type: str) -> str:
        """
        Utils method to save engine stats to file for later usage (in a nice graphical report by example)
        """
        directory_name = "data"

        # Check the data directory is free
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
        size: Number = os.path.getsize(file_path)
        while size > 1024 and suffix_index < 4:
            suffix_index += 1  # increment the index of the suffix
            size = size / 1024.0  # apply the division
        human_readable_size = "%.*f%s" % (2, size, suffixes[suffix_index])

        print(f"population saved into {os.path.abspath(file_path)}" f" File size : {human_readable_size}")

        return os.path.abspath(file_path)
