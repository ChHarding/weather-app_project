import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd

import matplotlib.pyplot as plt

class ProgressPlotter(tk.Tk):
    def __init__(self):
        super().__init__()

        self.df = pd.DataFrame({
            'hours': pd.date_range(start='2022-01-01', end='2022-01-02', freq='h'),
            'temperature': [10, 12, 14, 15, 16, 18, 20, 22, 23, 22, 20, 18, 16, 15, 14, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        })  

        self.progress_plot_frame = ttk.Frame(self)
        self.progress_plot_frame.pack(fill=tk.BOTH, expand=True)

        fig = plt.Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(self.df['hours'], self.df['temperature'], marker='o')

        ax.tick_params(axis='x', rotation=-45)

        canvas = FigureCanvasTkAgg(fig, master=self.progress_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self.progress_plot_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


if __name__ == '__main__':
    app = ProgressPlotter()
    app.mainloop()
