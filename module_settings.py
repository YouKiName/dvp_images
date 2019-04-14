import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk

import database as db

# --------------------------------
# Created by YouKiName
# 02.12.2018
# --------------------------------


class WindowSettings(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)

        self.title('Settings')
        self.geometry('400x400+400+300')
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        tab_control = ttk.Notebook(self)
        tab_control.pack(fill=tk.BOTH, expand=1)

        frame_folders = tk.Frame(tab_control)
        frame_images = tk.Frame(tab_control)
        frame_tegs = tk.Frame(tab_control)

        tab_control.add(frame_folders, text="Folders")
        tab_control.add(frame_images, text="Images")
        tab_control.add(frame_tegs, text="Tegs")

        # --------------------------------------------------
        # Frame Folders
        # Button Add Folder
        btn_add_folder = ttk.Button(frame_folders, text="Add Folder", command=self.add_folder_db)
        btn_add_folder.place(x=10, y=20)
        btn_select_folder = ttk.Button(frame_folders, text="Browse", command=self.open_folder)
        btn_select_folder.place(x=120, y=20)
        self.entry_folder = ttk.Entry(frame_folders, width=40, font=15)
        self.entry_folder.place(x=10, y=60)

        # Button change folder
        self.btn_change_folder = ttk.Button(frame_folders, text='Change', command=self.change_folder)
        # Button delete folder
        self.btn_delete_folder = ttk.Button(frame_folders, text='Delete', command=self.delete_folder)

        # Table
        self.selected_folder = None
        self.table_tree = ttk.Treeview(frame_folders, columns=('id', 'folder'), height=8, show='headings')
        self.table_tree.bind("<Double-Button-1>", self.select_folder)
        self.table_tree.place(x=10, y=100)
        self.table_tree.column('id', minwidth=5, width=25)
        self.table_tree.column('folder', minwidth=80, width=200)
        self.table_tree.heading('folder', text='Folders in DB')
        # Button Download image
        btn_download_images = ttk.Button(frame_folders, text="Download Images", command=self.download_image)
        btn_download_images.place(x=240, y=100)
        # Button Refresh
        btn_refresh = ttk.Button(frame_folders, text="Refresh", command=self.refresh_folders)
        btn_refresh.place(x=10, y=290)
        self.refresh_folders()
        # --------------------------------------------------
        # Frame Images
        lb_title_url = ttk.Label(frame_images, text="Adding images from url:\n"
                                                    "Warning: link should start with 'http://' or 'https://'", font=20)
        lb_title_url.pack(padx=20, pady=10, anchor=tk.W)
        lb_url = ttk.Label(frame_images, text="Enter url:", font=18)
        lb_url.pack(padx=20, pady=10, anchor=tk.W)
        self.entry_url = ttk.Entry(frame_images, font=15)
        self.entry_url.pack(fill=tk.X, padx=20, pady=0, anchor=tk.W)
        btn_add_url = ttk.Button(frame_images, text="Add", width=20,
                                 command=lambda: self.add_img_from_url(self.entry_url.get()))
        btn_add_url.pack(padx=20, pady=10, anchor=tk.W)

        # --------------------------------------------------
        # Frame Tegs
        self.selected_teg = None
        # Button Clear teg
        btn_clear_teg = ttk.Button(frame_tegs, text="Clear tegs", command=self.clear_tegs)
        btn_clear_teg.place(x=10, y=10)
        # Label hint
        hint = ttk.Label(frame_tegs, text='This button will delete all tegs which disused')
        hint.place(x=100, y=14)
        # Table with tegs
        tegs_title = ttk.Label(frame_tegs, text="Tegs", font=12)
        tegs_title.place(x=10, y=40)
        self.table_teg = tk.Listbox(frame_tegs, font=10, height=12)
        self.table_teg.bind("<Double-Button-1>", self.select_teg)
        self.table_teg.place(x=10, y=65)
        self.refresh_teg()
        # Button delete teg
        self.btn_del_teg = ttk.Button(frame_tegs, text='Delete', command=self.delete_teg)

    # FOLDERS ---------------

    def open_folder(self):
        folder = fd.askdirectory(title='Select Folder')
        if folder != "":
            self.entry_folder.delete(0, tk.END)
            self.entry_folder.insert(0, folder)

    def add_folder_db(self):
        direct = self.entry_folder.get()
        already_exist = False
        if direct != '' and direct is not None:
            already_exist = not db.add_folder(str(direct))

        if already_exist:
            info = "This folder already was added to DB."
            messagebox.showinfo(title="Warning", message=info)

        self.refresh_folders()

    def select_folder(self, event):
        cur_item = self.table_tree.focus()
        item = self.table_tree.item(cur_item)
        self.selected_folder = item['values']
        if not item['values']:
            return
        self.entry_folder.delete(0, 'end')
        self.entry_folder.insert(0, item['values'][1])
        self.btn_change_folder.place(x=240, y=140)  # view btn change
        self.btn_delete_folder.place(x=240, y=170)  # view btn delete

    def change_folder(self):
        folder = self.entry_folder.get()
        id = self.selected_folder[0]
        if folder != '' and folder is not None and id is not None:
            db.change_folder_name(id=id, folder=folder)
        self.refresh_folders()
        self.hide_special_btn_f()
        self.entry_folder.delete(0, 'end')

    def delete_folder(self):
        folder = self.entry_folder.get()
        answer = messagebox.askyesno("Delete folder", "Delete folder: {}?\n".format(folder))
        if not answer: return

        answer_del_im = messagebox.askyesno("Delete folder", "Delete ALL images from this folder too?\n"
                                                      "(Only images in database will be deleted,\n"
                                                      "images on disk will not be deleted.)")
        count = db.delete_folder(folder=folder, del_images=answer_del_im)
        if answer_del_im:
            info = "Success!\n{0} images was deleted.".format(count)
            messagebox.showinfo(title="Delete folder", message=info)
        self.refresh_folders()

    def download_image(self):
        cur_item = self.table_tree.focus()
        item = self.table_tree.item(cur_item)
        direct = str(item['values'][1])
        if direct != '':
            db_return = db.add_all_image(direct)
            info = "Success!\nDir: {dir}\nAdded images: {count}".format(dir=db_return[0], count=db_return[1])
            messagebox.showinfo(title="Adding images", message=info)

    def refresh_folders(self):
        self.table_tree.delete(*self.table_tree.get_children())
        folders = db.get_list_folder()
        for folder in folders:
            self.table_tree.insert('', 'end', values=folder)
        self.hide_special_btn_f()
        self.entry_folder.delete(0, 'end')

    def hide_special_btn_f(self):
        self.btn_change_folder.place_forget()
        self.btn_delete_folder.place_forget()

    # Images ----------------

    def add_img_from_url(self, url):
        if url and url != '':
            db.add_img_from_url(url)
            messagebox.showinfo(title="Adding url", message="Success!")
            self.entry_url.delete(0, 'end')
    # TEGS ------------------

    def refresh_teg(self):
        tegs = db.get_list_tegs()
        self.table_teg.delete(0, 'end')
        for teg in tegs:
            str_teg = "{0}, {1}".format(teg[0], teg[2])
            self.table_teg.insert('end', str_teg)

    def select_teg(self, event):
        cur_item = self.table_teg.curselection()[0]
        item = self.table_teg.get(cur_item).split(', ')
        self.selected_teg = item[0]
        self.show_special_btn_t()

    def clear_tegs(self):
        answer = messagebox.askyesno("Clear tegs", "This function delete all teg which disused.\nClear tegs?")
        if answer:
            count = db.clear_teg()
            info = "Success!\n{0} tegs was deleted.".format(count)
            messagebox.showinfo(title="Clear tegs", message=info)
        self.refresh_teg()

    def delete_teg(self):
        if self.selected_teg is None: return
        teg = self.selected_teg
        answer = messagebox.askyesno("Delete teg", "Delete teg: {}?\n"
                                                   "This teg will be removed from ALL\nimages in database!".format(teg))
        if answer:
            db.delete_teg_for_all(teg)
            info = "Success!"
            messagebox.showinfo(title="Delete teg", message=info)
        self.hide_special_btn_t()
        self.refresh_teg()

    def show_special_btn_t(self):
        self.btn_del_teg.place(x=200, y=65)

    def hide_special_btn_t(self):
        self.btn_del_teg.place_forget()

