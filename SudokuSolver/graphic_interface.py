"""
This page is used to configure the program GUI
"""

import pickle
import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from SudokuSolver.grids import small_6x6_112


class Frame(tk.Frame):
    """
    Class used for create un new frame. Useful to share information between classes.
    """

    def __init__(self, individual=None, individual_cursor=0, generation_cursor=0, given_cells=None, **kwargs):
        super().__init__()
        self.individual = individual
        self.individual_cursor = tk.IntVar(individual_cursor)
        self.generation_cursor = tk.IntVar(generation_cursor)
        self.given_cells = given_cells

        self.mean_score = tk.IntVar(0)
        self.max_score = tk.IntVar(0)
        self.min_score = tk.IntVar(0)

        self.init_ui(**kwargs)

    def init_ui(self, **kwargs):
        """
        This abstract method is the ui constructor.
        """
        raise NotImplemented


class Header(Frame):
    """
    Show the title
    """

    def init_ui(self, **kwargs):
        tk.Label(self, text="Résolution d'un sudoku", font=('Helvetica', 20), height=5).pack(side=tk.TOP)
        self.pack()


class Sodoku(Frame):
    """
    Display the sudoku frame. The bold numbers are the numbers by default.
    """

    x_separator = 3
    y_separator = 3

    def init_ui(self, sep_index=2, **kwargs):
        self.x_separator = sep_index
        self.y_separator = sep_index if sep_index % 3 == 0 else sep_index + 1

        for cell in self.given_cells:
            font = ('Helvetica', 13, 'bold')
            self.place_cell(cell.position.coordinates[0], cell.position.coordinates[1], cell.value, font)

        self.fill()
        self.configure(bg='black')

    def fill(self):
        """
        Method used to place the rest of the cells
        """
        for cell in self.individual.cells - self.given_cells:
            self.place_cell(cell.position.coordinates[0], cell.position.coordinates[1], cell.value, ('Helvetica', 13))

        self.pack()

    def place_cell(self, row, column, cell_value, font):
        """
        Method used to place the cells predicted by the algorithm
        """
        cell_label = tk.Label(self, text=cell_value, width=2, borderwidth=2, relief='groove', font=font)
        cell_label.grid(
            row=row, column=column,
            pady=(4 if row % self.x_separator == 0 and row else 1, 0),
            padx=(4 if column % self.y_separator == 0 and column else 1, 0),
        )


class Cursor(Frame):
    """
    Show buttons to change the generation and display the current individual.
    """

    def init_ui(self, next_gen, previous_gen, **kwargs):
        frame = tk.Frame(self)
        tk.Label(frame, text='Génération', font=('Helvetica', 14)).pack()
        tk.Label(frame, textvariable=self.generation_cursor, font=('Helvetica', 17)).pack()
        frame.pack(padx=30, side=tk.LEFT)

        frame = tk.Frame(self)
        tk.Label(frame, text='Meilleur Individu', font=('Helvetica', 14)).pack()
        tk.Label(frame, textvariable=self.individual_cursor, font=('Helvetica', 17)).pack()
        frame.pack(padx=30, side=tk.RIGHT)

        frame = tk.Frame()
        tk.Button(frame, text='<', command=previous_gen).pack(side=tk.LEFT)
        tk.Button(frame, text='>', command=next_gen).pack(side=tk.RIGHT)
        frame.pack()

        self.pack(pady=15)


class Score(Frame):
    """
    Show minimum, average and maximum scores of the current generation.
    """

    def init_ui(self, **kwargs):
        self.line('Score minimum de la generation: ', 'min_score')
        self.line('Score moyen de la generation: ', 'mean_score')
        self.line('Score maximum de la generation: ', 'max_score')

        self.pack()

    def line(self, text, variable):
        """
        Each lines corresponds to a specific statistic.
        """
        frame = tk.Frame(self)
        tk.Label(frame, text=text, font=('Helvetica', 14)).pack(side=tk.LEFT)
        tk.Label(frame, textvariable=getattr(self, variable), font=('Helvetica', 14), ).pack(side=tk.RIGHT)
        frame.pack(pady=5)


class Graph(Frame):
    """
    Show the dynamic graphic. It is updated at each change of generation.
    """
    fig = plt.figure(facecolor=(0.851, 0.851, 0.851))
    canvas = None

    def init_ui(self, statistics, **kwargs):
        plt.ylabel('Score')
        plt.xlabel('Génération')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.update_graph(statistics)
        self.canvas.get_tk_widget().pack()
        self.pack()

    def update_graph(self, statistics):
        """
        Method used to update the graphic canvas
        """
        plt.clf()

        plt.plot([i[0] for i in statistics], marker='o')
        plt.plot([i[1] for i in statistics], marker='o')
        plt.plot([i[2] for i in statistics], marker='o')

        plt.legend(['Max', 'Mean', 'Min'], loc='upper left')
        plt.xlabel('Génération')
        plt.ylabel('Score')
        self.canvas.draw()


class UI(tk.Tk):
    """
        Main class of the gui.
    """

    def __init__(self, title, config, **kwargs):
        super().__init__(**kwargs)

        self.minsize(500, 600)
        self.title(title)
        self.config = config

        with open(config['populations_save'], 'rb') as pop_file:
            self.individuals = pickle.load(pop_file)

        with open(config['statistics'], 'rb') as stats_file:
            self.statistics = pickle.load(stats_file)

        max_cell = sorted(config['given_cells'], key=lambda cell: cell.position.coordinates[0])[-1]
        grid_size = (max_cell.position.coordinates[0] + 1) / 3

        self.Header = Header()
        self.Sodoku = Sodoku(sep_index=grid_size, individual=self.individuals[0], given_cells=config['given_cells'])
        self.Cursor = Cursor(
            next_gen=lambda: self.update_generation(self.Cursor.generation_cursor.get() + 1),
            previous_gen=lambda: self.update_generation(self.Cursor.generation_cursor.get() - 1)
        )

        self.Score = Score()
        self.Graph = Graph(statistics=self.statistics)

        self.update_generation(0)

    def update_generation(self, new_gen_cursor):
        """
        Method call when the current generation has changed.
        """
        try:
            individual = self.individuals[new_gen_cursor]
        except IndexError:
            individual = self.individuals[0]
            new_gen_cursor = 0

        generation_stats = self.statistics[new_gen_cursor]
        self.Sodoku.individual = individual
        self.Cursor.generation_cursor.set(new_gen_cursor)
        self.Cursor.individual_cursor.set(generation_stats[3])

        self.Score.max_score.set(round(generation_stats[0], 2))
        self.Score.mean_score.set(round(generation_stats[1], 2))
        self.Score.min_score.set(round(generation_stats[2], 2))

        self.Graph.update_graph(self.statistics[:new_gen_cursor + 1])

        self.Sodoku.fill()

    def show(self):
        self.mainloop()


if __name__ == '__main__':
    UI('Sudoku',
       {'populations_save': './data/population_sudoku_2019-11-20_10:35:44.350536',
        'statistics': './data/stats_sudoku_2019-11-20_10:35:44.350282',
        'given_cells': small_6x6_112,
        }).show()
