import tkinter as tk
from tkinter import ttk
import database as db

# --------------------------------
# Created by YouKiName
# 02.12.2018
# --------------------------------


class WindowTegs(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title('Choice tegs')
        self.geometry('400x500+400+300')
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        # Create table with all tegs
        self.tree_all = ttk.Treeview(self, columns=('teg', 'count'), height=20, show='headings')
        self.tree_all.bind("<Double-Button-1>", self.select_teg)
        self.tree_all.place(x=10, y=10)
        self.tree_all.column("teg", width=150)
        self.tree_all.column("count", width=50)
        self.tree_all.heading("teg", text="Teg")
        self.tree_all.heading("count", text="Count")

        all_tegs = db.get_list_tegs()
        for teg in all_tegs:
            self.tree_all.insert('', 'end', values=(teg[0], teg[2]))

        # Create table with all tegs
        self.tree_choose = ttk.Treeview(self, columns='teg', height=20, show='headings')
        self.tree_choose.bind("<Double-Button-1>", self.remove_teg)
        self.tree_choose.place(x=230, y=10)
        self.tree_choose.column("teg", width=150)
        self.tree_choose.heading("teg", text="Teg")

        # Button
        btn_select = ttk.Button(self, text='Choose', command=self.choose)
        btn_select.place(x=305, y=455)

    def select_teg(self, event):
        cur_item = self.tree_all.focus()
        item = self.tree_all.item(cur_item)
        if not item['values']:
            return
        self.tree_choose.insert('', 'end', values=item['values'][0])

    def remove_teg(self, event):
        focus_t = self.tree_choose.focus()
        if focus_t != '':
            self.tree_choose.delete(focus_t)

    def choose(self):
        childs = self.tree_choose.get_children()
        self.items = []
        self.items.clear()
        for child in childs:
            item = self.tree_choose.item(child)['values'][0]
            self.items.append(item)





