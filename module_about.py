import tkinter as tk
from tkinter import ttk

# --------------------------------
# Created by YouKiName
# 02.12.2018
# --------------------------------


class WindowSettings(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title('About')
        self.geometry('400x400+400+300')
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        title = ttk.Label(self, text="DVP Images", font=("Helvetica", 30, "bold italic"))
        title.place(x=80, y=10)
        sep_top = ttk.Separator(self)
        sep_top.place(x=0, y=70, relwidth=2)

        version = ttk.Label(self, text="Version: 1.3(Alpha)", font=("Helvetica", 15))
        version.place(x=20, y=90)

        info = "Changes:\n" \
               "- New visual design\n" \
               "- New interface of choice tegs\n" \
               "- Improving window of settings\n" \
               "- Added function delete folder\n" \
               "- Added function delete teg from all images"
        label_info = ttk.Label(self, text=info, font=("Helvetica", 12))
        label_info.place(x=25, y=130)

        sep_bot = ttk.Separator(self)
        sep_bot.place(x=0, y=330, relwidth=2)
        # E-Mail
        mail = ttk.Label(self, text="Email: youkiname@mail.ru", font=("Helvetica", 10), foreground='blue')
        mail.place(x=5, y=376)

        # Developer info
        develop_1 = ttk.Label(self, text="Develop since December 2, 2018", font=("Helvetica", 12, 'italic'))
        develop_1.place(x=30, y=340)
        develop_2 = ttk.Label(self, text="By YouKiName", font=("Helvetica", 12, 'italic'))
        develop_2.place(x=270, y=368)
