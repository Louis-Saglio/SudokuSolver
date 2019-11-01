from genetic import run, save_population_to_file
from string_match import String


def main():
    save_population_to_file(run(String, 100, lambda p, mini, avg, maxi: maxi == 100, "initial string"))


if __name__ == "__main__":
    main()
