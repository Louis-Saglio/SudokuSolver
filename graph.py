import pickle
import tkinter as tk


class Frame(tk.Frame):
    def __init__(self, individual=None, individual_cursor=0, generation_cursor=0, **kwargs):
        super().__init__()
        self.individual = individual
        self.individual_cursor = tk.IntVar(individual_cursor)
        self.generation_cursor = tk.IntVar(generation_cursor)
        self.init_ui(individual=individual, **kwargs)

    def init_ui(self, **kwargs):
        raise NotImplemented


class Header(Frame):
    def init_ui(self, **kwargs):
        tk.Label(self, text="Résolution d'un sudoku", font=('Helvetica', 20), height=5).pack(side=tk.TOP)
        self.pack()


class Sodoku(Frame):
    def init_ui(self, **kwargs):
        for cell in self.individual.cells:
            row = cell.position.coordinates[0]
            column = cell.position.coordinates[1]

            value = tk.StringVar()
            value.set(cell.value)

            cell_label = tk.Label(self, textvariable=value, width=2, borderwidth=2, relief="groove",
                                  font=('Helvetica', 12))
            cell_label.grid(
                row=row, column=column,
                pady=(4 if row % 3 == 0 and row else 1, 0),
                padx=(4 if column % 3 == 0 and column else 1, 0),
            )

        self.configure(bg='black')
        self.pack(side=tk.TOP)


class Cursor(Frame):
    def init_ui(self, next_ind, next_gen, previous_ind, previous_gen, **kwargs):
        self._generate_carousel('Génération', self.generation_cursor, tk.LEFT, next_gen, previous_gen)
        self._generate_carousel('Individu', self.individual_cursor, tk.RIGHT, next_ind, previous_ind)

        self.pack(pady=30, side=tk.TOP)

    def _generate_carousel(self, title, value, side, next_callback, previous_callback):
        frame = tk.Frame(self)
        tk.Label(frame, text=title, font=('Helvetica', 14)).pack()

        tk.Button(frame, text='<', command=previous_callback).pack(side=tk.LEFT)
        tk.Label(frame, textvariable=value, font=('Helvetica', 17)).pack(side=tk.LEFT)
        tk.Button(frame, text='>', command=next_callback).pack(side=tk.RIGHT)
        frame.pack(pady=20, padx=30, side=side)


class Score(Frame):
    def init_ui(self, **kwargs):
        tk.Label(self, text='Score du meilleur individu: a', font=('Helvetica', 14), pady=5).pack()
        tk.Label(self, text='Score moyen de la generation a', font=('Helvetica', 14)).pack()

        self.pack(side=tk.BOTTOM)


class UI(tk.Tk):
    def __init__(self, title, config, **kwargs):
        super().__init__(**kwargs)

        self.minsize(500, 600)
        self.title(title)

        with open(config['populations_save'], 'rb') as file:
            self.individuals = pickle.load(file)
            print("Best solution of last population:")
            print(sorted(self.individuals[-1], key=lambda i: i.normalized_rate())[-1])

        self.Header = Header()
        self.Sodoku = Sodoku(individual=self.individuals[0][0])
        self.Cursor = Cursor(individual_cursor=0, generation_cursor=0,
                             next_ind=self.next_individual, previous_ind=self.previous_individual,
                             next_gen=self.next_generation, previous_gen=self.previous_generation)
        self.Score = Score()

    def next_individual(self):
        gen_cursor, ind_cursor = self.get_cursors()

        self.Sodoku.individual = self.individuals[gen_cursor][ind_cursor + 1]
        self.Sodoku.init_ui()

        self.Cursor.individual_cursor.set(ind_cursor + 1)

    def previous_individual(self):
        gen_cursor, ind_cursor = self.get_cursors()

        self.Sodoku.individual = self.individuals[gen_cursor][ind_cursor - 1]
        self.Sodoku.init_ui()

        self.Cursor.individual_cursor.set(ind_cursor - 1)

    def next_generation(self):
        self.update_generation(self.Cursor.generation_cursor.get() + 1)

    def previous_generation(self):
        self.update_generation(self.Cursor.generation_cursor.get() - 1)

    def update_individual(self, new_ind_cursor):
        gen_cursor = self.Cursor.generation_cursor.get()

        try:
            individual = self.individuals[gen_cursor][new_ind_cursor]
        except IndexError:
            individual = self.individuals[gen_cursor][0]
            new_ind_cursor = 0

        self.Sodoku.individual = individual
        self.Cursor.individual.set(new_ind_cursor)
        self.Sodoku.init_ui()

    def update_generation(self, new_gen_cursor):
        ind_cursor = self.Cursor.individual_cursor.get()

        try:
            individual = self.individuals[new_gen_cursor][ind_cursor]
        except IndexError:
            individual = self.individuals[0][ind_cursor]
            new_gen_cursor = 0

        self.Sodoku.individual = individual
        self.Cursor.generation_cursor.set(new_gen_cursor)
        self.Sodoku.init_ui()

    def get_cursors(self):
        return self.Cursor.generation_cursor.get(), self.Cursor.individual_cursor.get()

    def show(self):
        self.mainloop()


if __name__ == '__main__':
    UI('Sudoku', {'populations_save': './data/list_64.91028037383178_2019-11-08_10:14:43.738971'}).show()
