import pickle
import tkinter as tk

from sudoku import Sudoku

LOGS_PATH = './data/list_77.75467289719626_2019-11-07_14:56:33.138436'


class Frame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_ui()

    @staticmethod
    def populations():
        with open(LOGS_PATH, 'rb') as file:
            return pickle.load(file)[1]

    def init_ui(self):
        raise NotImplemented


class Header(Frame):
    def init_ui(self):
        tk.Label(self, text="Résolution d'un sudoku", font=('Helvetica', 20), height=5).pack(side=tk.TOP)
        self.pack()


class Sodoku(Frame):
    def init_ui(self):
        population: Sudoku = self.populations()[-1]

        for cell in population.cells:
            row = cell.position.coordinates[0]
            column = cell.position.coordinates[1]

            temp = tk.Label(self, text=cell.value, width=2, borderwidth=2, relief="groove", font=('Helvetica', 12))
            temp.grid(
                row=row, column=column,
                pady=(4 if row % 3 == 0 and row else 1, 0),
                padx=(4 if column % 3 == 0 and column else 1, 0),
            )

        self.configure(bg='black')
        self.pack(side=tk.TOP)


class Cursor(Frame):
    def init_ui(self):
        self.generate_carousel('Génération', 1, tk.LEFT)
        self.generate_carousel('Population', 1, tk.RIGHT)

        self.pack(pady=30)

    def generate_carousel(self, title, value, side):
        frame = tk.Frame(self)
        tk.Label(frame, text=title, font=('Helvetica', 14)).pack()

        tk.Button(frame, text='<').pack(side=tk.LEFT)
        tk.Label(frame, text=value, font=('Helvetica', 17)).pack(side=tk.LEFT)
        tk.Button(frame, text='>').pack(side=tk.RIGHT)
        frame.pack(pady=20, padx=30, side=side)


class Score(Frame):
    def init_ui(self):
        tk.Label(self, text='Score du meilleur individu: a', font=('Helvetica', 14), pady=5).pack()
        tk.Label(self, text='Score moyen de la population a', font=('Helvetica', 14)).pack()

        self.pack()


class UI(tk.Tk):
    def __init__(self, title, **kwargs):
        super().__init__(**kwargs)

        self.minsize(500, 600)
        self.title(title)

        self.Header = Header()
        self.Sodoku = Sodoku()
        self.Population = Cursor()
        self.Score = Score()

    def show(self):
        self.mainloop()


if __name__ == '__main__':
    UI('Sudoku').show()
