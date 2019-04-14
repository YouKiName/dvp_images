import io
import os
import threading as thr
import urllib.request
from tkinter import *
from tkinter import simpledialog
from tkinter import ttk

from PIL import ImageTk, Image
from memory_profiler import memory_usage

import colors
import database as db
import module_about
import module_settings
import search as s

# --------------------------------
# Created by YouKiName
# 02.12.2018
# --------------------------------

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


class MainWindow:
    color1 = colors.color_bg
    color2 = colors.color_bg2

    def __init__(self, root):
        self.root = root
        self.root.minsize(1050, 630)
        self.root.bind("<space>", lambda event: print(memory_usage()))
        # Style
        ttk.Style().layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders
        ttk.Style().configure("Main.TSeparator", background=colors.sep)
        ttk.Style().configure("TNotebook", background=colors.notebook)

        # Menu
        main_menu = Menu(root)
        # File Menu
        file_menu = Menu(main_menu, tearoff=0)
        file_menu.add_command(label='Open')
        file_menu.add_command(label='Save as')
        # Main Menu
        main_menu.add_cascade(label='File', menu=file_menu)
        main_menu.add_command(label='Settings', command=self.open_settings)
        main_menu.add_command(label='Refresh', command=self.main_refresh)
        main_menu.add_command(label='Search...', command=self.advanced_search)
        main_menu.add_command(label='About', command=self.open_about)

        self.root.config(menu=main_menu)

        frame_left = Frame(root, bg=self.color1, bd=5, width=500)
        frame_center = Frame(root, bg=self.color1, bd=5)
        frame_right = Frame(root, bg=self.color1, bd=5)

        frame_left.pack(side='left', fill=Y, expand=0, padx=0)
        frame_center.pack(side='left', fill=Y, expand=0, padx=0)
        frame_right.pack(side='right', fill=BOTH, expand=1, padx=0)

        # Frame 1 - LEFT
        title_tegs = Label(frame_left, text="TEGS", font=("Helvetica", 15, "bold"), bg=colors.label, fg=colors.text_lb1)
        title_tegs.pack(side=TOP, fill=X)

        frame_left_top = Frame(frame_left)
        frame_left_top.pack(side=TOP, fill=BOTH, expand=1)

        teg_scroll_1 = Scrollbar(frame_left_top, width=10)
        teg_scroll_1.pack(side=LEFT, fill=Y, expand=0, pady=0)

        self.table_tegs = ttk.Treeview(frame_left_top, columns=('teg', 'count'), height=5,
                                       show='headings', yscrollcommand=teg_scroll_1.set)
        self.table_tegs.bind("<Double-Button-1>", self.select_teg)
        self.table_tegs.pack(side=TOP, fill=BOTH, expand=1, padx=(0, 0), pady=5)
        self.table_tegs.column('teg', minwidth=70, width=90)
        self.table_tegs.heading('teg', text='Teg')
        self.table_tegs.column('count', minwidth=40, width=20)
        self.table_tegs.heading('count', text='Count')
        teg_scroll_1.config(command=self.table_tegs.yview)

        btn_search = Button(frame_left, width=15, text='Search', relief=FLAT, font=15, bg=colors.button,
                            fg=colors.text_btn, command=self.search)
        btn_search.pack(side=BOTTOM, fill=X, pady=3, padx=0)

        self.selected_teg_list = Listbox(frame_left, height=10, font=9)
        self.selected_teg_list.pack(side=BOTTOM, fill=BOTH, expand=0, padx=0, pady=0)
        self.selected_teg_list.bind("<Double-Button-1>", self.remove_teg_left_list)

        btn_desel_all = Button(frame_left, relief=FLAT, width=10, text="Deselect All",
                               bg=colors.button, fg=colors.text_btn, font=4, command=self.deselect_all_tegs)
        btn_desel_all.pack(fill=X, padx=0, pady=3)

        # -----------------

        # Frame 2 - CENTER
        self.selected_image = None  # file PIL.Image.open()
        self.id_select_image = None
        self.name_select_image = None
        self.desc_select_image = None
        self.dir_select_image = None
        self.link_select_image = None

        sep_left = ttk.Separator(frame_center, orient=VERTICAL, style="Main.TSeparator")
        sep_left.pack(side=LEFT, fill=Y, expand=1, padx=(0, 5), pady=0, anchor=W)

        title_images = Label(frame_center, text="Images", font=("Helvetica", 15, "bold"),
                             bg=colors.label, fg=colors.text_lb1)
        title_images.pack(side=TOP, fill=X)
        i_scroll = Scrollbar(frame_center)
        i_scroll.pack(side=RIGHT, fill=Y)
        self.image_table = ttk.Treeview(frame_center, columns=('id', 'name', 'loc'), height=20,
                                        show='headings', yscrollcommand=i_scroll.set)
        self.image_table.pack(side=TOP, fill=Y, expand=1)
        i_scroll.config(command=self.image_table.yview)
        self.root.bind("<Down>", lambda event: self.set_select_tree(event=event, key='next'))
        self.root.bind("<Up>", lambda event: self.set_select_tree(event=event, key='prev'))
        self.image_table.bind("<Double-Button-1>", self.select_image)
        self.image_table.column('id', minwidth=20, width=30)
        self.image_table.heading('id', text='Id')
        self.image_table.column('name', minwidth=100, width=150)
        self.image_table.heading('name', text='Name')
        self.image_table.column('loc', minwidth=80, width=120)
        self.image_table.heading('loc', text='Loc')
        # -----------------
        # FRAME 3 - RIGHT
        # Thread for download image:
        self.thread_load_image = None
        self.load_allow = True
        # -> Additional Frame for tegs and buttons
        frame_r_top1 = Frame(frame_right, bg=self.color1, bd=0)
        frame_r_top1.pack(side=TOP, anchor=N, fill=X, expand=0)
        frame_r_top2 = Frame(frame_right, bg=self.color1, bd=2)
        frame_r_top2.pack(side=TOP, anchor=N, fill=BOTH, expand=0)
        frame_r_top3 = Frame(frame_right, bg=self.color1, bd=2)
        frame_r_top3.pack(side=TOP, anchor=N, fill=X, expand=0)

        frame_r_bottom = Frame(frame_right, bg=self.color1, bd=2)
        frame_b_top = Frame(frame_r_bottom, bg=self.color1, bd=2)
        frame_b_left = Frame(frame_r_bottom, bg=self.color1, bd=5)
        frame_b_right = Frame(frame_r_bottom, bg=self.color1, bd=5)
        # Progress bar
        self.load_progress_bar = ttk.Progressbar(frame_r_top1, mode='determinate')
        self.load_progress_bar["maximum"] = 100
        # pop-up menu on right click
        self.change_menu = Menu(tearoff=0)
        self.change_menu.add_command(label="Change name", command=self.change_image_name)
        # Data image
        self.i_info = Label(frame_r_top2, text='', bg=colors.label, fg=colors.text_lb1, font=15)
        self.i_info.grid(column=0, row=0, sticky=W)
        self.i_name = Label(frame_r_top3, text='Name of Image: ', bg=colors.label, fg=colors.text_lb1, font=15)
        self.i_name.grid(column=0, row=0, sticky=W)
        self.i_name.bind("<Button-3>", self.popup_change_menu)
        self.i_dir = Label(frame_r_top3, text='Location of Image: ', bg=colors.label, fg=colors.text_lb1, font=15)
        self.i_dir.grid(column=0, row=1, sticky=W)
        btn_delete_image = Button(frame_r_top2, text='Remove image', relief=FLAT, bg=colors.button, fg=colors.text_btn,
                                  width=15, command=self.delete_image_db)
        btn_delete_image.grid(column=1, row=0, sticky=E, padx=10)
        # ---------------
        # Canvas
        self.canvas = Canvas(frame_right, width=500, height=200, bg=self.color1)
        self.canvas.pack(side=TOP, anchor=N, padx=30, pady=(10, 2), expand=1, fill=BOTH)
        self.canvas.bind('<Configure>', self._resize_handler_canvas)
        self.canvas.bind("<Double-Button-1>", self.open_image)
        self.not_found_image = Image.open(os.path.join(PROJECT_DIR, 'not_found.jpg')).resize((500, 300))
        self.loading_image = Image.open(os.path.join(PROJECT_DIR, 'loading.jpg')).resize((500, 300))
        self.photo_image = ImageTk.PhotoImage(self.not_found_image)
        self.canvas_image = self.canvas.create_image(0, 0, anchor=NW, image=self.photo_image)
        # ---------------------
        frame_r_bottom.pack(side=TOP, anchor=S, fill=BOTH, expand=0, pady=(10, 0), padx=10)
        tab_control = ttk.Notebook(frame_r_bottom, takefocus=False)
        tab_control.pack(fill=BOTH, expand=1)
        tab_tegs = Frame(tab_control, bg=self.color1)
        tab_desc = Frame(tab_control, bg=self.color1)
        tab_control.add(tab_tegs, text="Tegs")
        tab_control.add(tab_desc, text="Description")
        # Description ----------
        desc_title = Label(tab_desc, text="Description", font=("Helvetica", 15),
                           fg=colors.text_lb1, bg=colors.label)
        desc_title.pack()
        self.desc = Text(tab_desc, height=6, font=("Helvetica", 12),
                         bg=colors.text_input_bg, fg=colors.white)
        self.desc.pack(fill=X, padx=15, pady=5)

        # ----- Tegs -----------------------
        self.i_teg_title = Label(tab_tegs, text='TEGS: ', bg=colors.label,
                                 fg=colors.text_lb1, font=("Helvetica", 15, "bold"))
        self.i_teg_title.grid(row=0, column=0, padx=(10, 0))
        self.teg_list = Listbox(tab_tegs, font=12, height=8)
        self.teg_list.grid(row=1, column=0, padx=(10, 0), pady=(0, 5))

        self.btn_add_teg = Button(tab_tegs, width=10, text="Add Teg", relief=FLAT, bg=colors.button, fg=colors.text_btn, font=15, command=self.add_teg)
        self.btn_add_teg.grid(row=1, column=1, padx=5, pady=0, sticky=NW)
        self.add_entry = Entry(tab_tegs, width=20, font=17)
        self.add_entry.grid(row=1, column=2, padx=10, pady=(5, 0), sticky=NW)
        self.choose_teg = Button(tab_tegs, width=10, text="Choose tegs", relief=FLAT, bg=colors.button, fg=colors.text_btn, font=15, command=self.choice_teg)
        self.choose_teg.grid(row=1, column=2, padx=10, pady=35, sticky=NW)

        self.is_clear_teg = BooleanVar()
        check_clear_teg = Checkbutton(tab_tegs, text='Clear entry after adding', bg=self.color1, fg=colors.text_lb1,
                                      font=('Helvetica', 13), variable=self.is_clear_teg, onvalue=True, offvalue=False)
        check_clear_teg.select()
        check_clear_teg.grid(row=1, column=2, padx=5, pady=65, sticky=NW)
        self.btn_teg_del = Button(tab_tegs, width=10, text="Delete Teg", relief=FLAT, bg=colors.button,
                                  fg=colors.text_btn, font=15, command=self.delete_teg)
        self.btn_teg_del.grid(row=1, column=1, padx=5, pady=35, sticky=NW)
        # -----------------
        self.main_refresh()

    def _resize_handler_canvas(self, event):
        if self.selected_image is None:
            return
        self.photo_image = self.crop_image(self.selected_image)
        coord_x = int(self.canvas.winfo_width()/2 - self.photo_image.width()/2)
        self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
        self.canvas.coords(self.canvas_image, coord_x, 0)
        if event.width > 800:
            self.canvas.config(width=800)
        if event.height > 300:
            self.canvas.config(height=300)

    def get_select_tegs(self):
        """Return list of selected tegs"""
        cur_items = self.selected_teg_list.get(0, 'end')
        tegs = []
        for item in cur_items:
            teg = item.split(', ')[0]
            tegs.append(teg)
        return tegs

    def get_image_data_from_table(self):
        """Return list (id, name, tegs, description, dir, link) selected image"""
        cur_item = self.image_table.focus()
        item = self.image_table.item(cur_item)
        if not item['values']:
            return None
        data = db.get_image_by_id(item['values'][0])
        return data

    def get_image_from_url(self, url: str):
        """Take image's direct link
           Return file Image.open
           Return None if error was been or load was stopped"""
        def download_chunk(readsofar=0, chunk_size=1024):
            # report progress
            percent = readsofar * 100 / total_size  # assume total_size > 0
            self.load_progress_bar['value'] = int(percent)
            # download chunk
            data_chunk = http.read(chunk_size)
            if not data_chunk:  # finished downloading
                return None
            else:
                return data_chunk

        try:
            http = urllib.request.urlopen(url)
        except UnicodeEncodeError:
            print("Failed to load image!")
            print("The link should contains only latin letters and signs")
            print("URL: " + url)
            return None
        except urllib.error.URLError:
            print("Failed to load image!")
            print("Maybe link is wrong")
            print("URL: " + url)
            return None

        total_size = int(http.headers['Content-Length'])
        chunk_size = total_size / 100
        data_image = None
        i = 0
        while i < 101 and self.load_allow:
            if data_image is None:
                data_image = download_chunk(chunk_size=int(chunk_size))
            else:
                data_image += download_chunk(readsofar=len(data_image), chunk_size=int(chunk_size))
            i += 1

        if not self.load_allow:
            return None

        stream = io.BytesIO(data_image)
        return Image.open(stream)

    def deselect_all_tegs(self):
        self.selected_teg_list.delete(0, 'end')
        self.refresh_teg()

    def search(self):
        tegs = self.get_select_tegs()
        images = s.search(tegs)
        count = str(len(images))
        if not tegs or tegs is None:
            self.root.title("DVP  " + "Search ALL : " + count)
        else:
            self.root.title("DVP  " + "Search: " + str(tegs) + ' : ' + count)
        self.refresh_images(images)

    def advanced_search(self):
        tegs = simpledialog.askstring(title='Advanced Search', prompt='Enter Tegs: ')
        if tegs is None:
            return
        tegs = tegs.split(' ')
        images = s.advanced_search(tegs)
        count = str(len(images))
        if tegs is None:
            return
        self.root.title("DVP  " + "Search: " + str(tegs) + ' : ' + count)
        if tegs[0] == '':
            self.root.title("DVP  " + "Search without tegs" + ' : ' + count)
        self.refresh_images(images)

    def crop_image(self, image):
        """Take object from Image.open
           Return PhotoImage"""
        height = image.size[1]
        width = image.size[0]
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if height >= width:
            photo_height = int(canvas_height)
            photo_width = int(width / height * canvas_height)
        else:
            photo_width = int(canvas_width)
            photo_height = int(height / width * canvas_width)
            if photo_height > canvas_height:
                photo_height = int(canvas_height)
                photo_width = int(width / height * canvas_height)
        photo = image.resize((photo_width, photo_height))
        return ImageTk.PhotoImage(photo)

    def clean_image_info(self):
        # Clean labels
        self.i_info['text'] = ""
        self.i_name['text'] = ""
        self.i_dir['text'] = ""

    def select_teg(self, event):
        """Selects teg in table, adding her in listbox and remove it from table"""
        cur_item = self.table_tegs.focus()
        item = self.table_tegs.item(cur_item)
        if not item['values']:
            return
        teg = '{0}, {1}'.format(item['values'][0], item['values'][1])
        self.selected_teg_list.insert(END, teg)
        self.table_tegs.delete(cur_item)

    def draw_loading_image(self):
        self.photo_image = ImageTk.PhotoImage(self.loading_image)
        coord_x = int(self.canvas.winfo_width() / 2 - self.photo_image.width() / 2)
        self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
        self.canvas.coords(self.canvas_image, coord_x, 0)

    def draw_image_from_dir(self, name, loc):
        """Draw selected image in canvas(preview)
        Take name and loc of image
        Return False if error founding image
        or True if everything is ok
        """
        flag = True
        if name is None or loc is None:
            return None
        try:
            image = Image.open(loc + '/' + name)
            self.selected_image = image
            self.photo_image = self.crop_image(image)
        except FileNotFoundError:
            self.selected_image = self.not_found_image
            self.photo_image = ImageTk.PhotoImage(self.not_found_image)
            flag = False
        # Place image on center and Draw
        coord_x = int(self.canvas.winfo_width() / 2 - self.photo_image.width() / 2)
        self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
        self.canvas.coords(self.canvas_image, coord_x, 0)
        return flag

    def draw_image_by_link(self, link: str):
        """Draw selected image in canvas(preview)
        Take link of image
        Return False if error loading image
        or True if everything is ok
        """
        self.load_progress_bar.pack(side=TOP, fill=X)
        self.draw_loading_image()
        self.show_image_data_by_link("Downloading image...", self.link_select_image, False, False)
        image = self.get_image_from_url(link)
        if not self.load_allow:
            return
        if image is None:
            # Draw 'not_found' image
            self.selected_image = self.not_found_image
            self.photo_image = ImageTk.PhotoImage(self.not_found_image)
            self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
            error = True
        else:
            self.selected_image = image
            self.photo_image = self.crop_image(image)
            # Place image on center and Draw
            coord_x = int(self.canvas.winfo_width() / 2 - self.photo_image.width() / 2)
            self.canvas.itemconfig(self.canvas_image, image=self.photo_image)
            self.canvas.coords(self.canvas_image, coord_x, 0)
            error = False
        self.show_image_data_by_link(self.name_select_image, self.link_select_image, error)
        self.load_progress_bar.pack_forget()

    def show_image_data_by_link(self, name, link, error: bool, showinfo=True):
        self.clean_image_info()
        self.i_name['text'] = 'Name of Image: ' + name
        self.i_dir['text'] = 'Location of Image: ' + link
        if error:
            self.i_info['text'] = "Failed showing data"
        elif showinfo:
            image = self.selected_image
            try:
                self.i_info['text'] = "Resolution: {0} Dpi: {1} {2}".format(image.size, image.info['dpi'], image.format)
            except KeyError:
                self.i_info['text'] = "Resolution: {0} Dpi: {1} {2}".format(image.size, "Unknown", image.format)

    def show_image_data_by_dir(self, name, loc, error: bool):
        self.clean_image_info()
        self.i_name['text'] = 'Name of Image: ' + name
        self.i_dir['text'] = 'Location of Image: ' + loc
        if error:
            self.i_info['text'] = "Failed showing data"
        else:
            try:
                image = self.selected_image
                self.i_info['text'] = "Resolution: {0} Dpi: {1} {2}".format(image.size, image.info['dpi'], image.format)
            except KeyError:
                self.i_info['text'] = "Resolution: {0} Dpi: {1} {2}".format(image.size, "Unknown", image.format)

    def select_image(self, event):
        self.save_desc_image()
        data = self.get_image_data_from_table()
        if data is None:
            return None
        if self.id_select_image == data[0]:
            return None
        if data[4] is None:  # replace dir(data[4]) to link(data[5])
            link = data[5]  # link
            direct = data[5]
        else:
            link = None
            direct = data[4]  # dir folder
        # -------------------------------------------------------
        if direct[0:8].lower() == "https://" or direct[0:7].lower() == "http://":
            # Thread for download image by link, drawing it and showing data\
            if self.thread_load_image is not None and self.thread_load_image.isAlive():
                self.load_allow = False
                if thr.active_count() > 1:
                    thr.enumerate()[1].join()
            self.thread_load_image = thr.Thread(target=self.draw_image_by_link,
                                                args=(direct,), name="Load_thread")
            self.load_allow = True
            self.thread_load_image.start()
        else:
            error = not self.draw_image_from_dir(data[1], data[4])
            self.show_image_data_by_dir(data[1], data[4], error)

        # Initialize variables with image's data ---------------
        self.id_select_image = data[0]
        self.name_select_image = data[1]
        self.desc_select_image = data[3]
        self.link_select_image = link
        self.dir_select_image = direct
        # -------------------------------------------------------
        # Show description
        self.refresh_desc()
        # Show Teg
        self.refresh_teg_image()

    def set_select_tree(self, event, key=''):
        if key == '':
            return
        items = self.image_table.get_children()
        focus_t = self.image_table.focus()
        item_id = None
        if key == 'next':
            if focus_t == '':
                item_id = 0
            else:
                item_id = items.index(focus_t)
        if key == 'prev':
            if focus_t == '':
                item_id = -1
            else:
                item_id = items.index(focus_t)
        self.image_table.focus(items[item_id])
        self.image_table.selection_set(items[item_id])
        self.select_image(event=None)

    def save_desc_image(self, ):
        if self.id_select_image is None:
            return None
        description = self.desc.get(1.0, 'end')
        db.add_description(self.id_select_image, description)

    def add_teg(self, teg=None):
        """Add teg to image
        Take teg for adding
        """
        if teg is None:
            teg = self.add_entry.get()
        if self.id_select_image is not None:
            if teg != '':
                db.add_teg_to_image(self.id_select_image, teg)
                if self.is_clear_teg.get():
                    self.add_entry.delete(0, 'end')
                self.refresh_teg_image()
                self.refresh_teg()

    def remove_teg_left_list(self, event):
        try:
            cur_item = self.selected_teg_list.curselection()[0]
            item = self.selected_teg_list.get(cur_item).split(', ')

            self.table_tegs.insert('', 'end', values=(item[0], item[1]))
            self.selected_teg_list.delete(cur_item)
        except IndexError:  # when no tegs in list
            pass

    def delete_teg(self):
        """Delete selected teg from teg_list"""
        if self.id_select_image is not None:
            cur_item = self.teg_list.curselection()
            if len(cur_item) != 0:
                teg = self.teg_list.get(cur_item[0])
                if teg != '':
                    db.delete_teg_from_image(self.id_select_image, teg)
            self.refresh_teg_image()
            self.refresh_teg()

    def delete_all_tegs(self):
        """Delete all tegs from teg_list"""
        pass

    def delete_image_db(self):
        if self.id_select_image is not None:
            db.delete_image(self.id_select_image)
            cur_item = self.image_table.focus()
            self.image_table.delete(cur_item)

    def choice_teg(self):
        tegs = self.get_select_tegs()
        if tegs:
            teg_str = ''
            for teg in tegs:
                if teg_str == '':
                    teg_str = teg
                else:
                    teg_str = teg_str + ', ' + teg
            self.add_entry.delete(0, END)
            self.add_entry.insert(0, teg_str)

    def change_image_name(self):
        id = self.id_select_image
        new_name = simpledialog.askstring(title='Change name', prompt='Enter new name: ')

        # changes name in explorer
        if self.link_select_image is None:
            path = self.dir_select_image
            name = self.name_select_image
            os.rename(path+'/'+name, path+'/'+new_name)
        # changes name in database
        db.change_name_image(id, new_name)
        self.i_name['text'] = 'Name of Image: {}'.format(new_name)
        # edit name in table
        self.edit_row_table_image(name=new_name)
        self.name_select_image = new_name

    def edit_row_table_image(self, img_id=None, name=None, loc=None):
        cur_item = self.image_table.focus()
        item = self.image_table.item(cur_item)
        if img_id is None:
            img_id = item['values'][0]
        if name is None:
            name = item['values'][1]
        if loc is None:
            loc = item['values'][2]
        new_values = (img_id, name, loc)
        index = int(str(cur_item)[1:], 16)  # convert from 16 base to decimal number
        self.image_table.insert("", index, values=new_values)
        self.image_table.delete(cur_item)

    def refresh_images(self, images):
        """Refresh table of image's name
        Take list of images
        """
        self.image_table.delete(*self.image_table.get_children())
        if not images:
            return
        for image in images:
            if image[4] is None:
                loc = image[5]  # loc = link
            else:
                loc = image[4].split('/')
                loc = str(loc[0] + '/....' + loc[-2] + '/' + loc[-1])
            self.image_table.insert('', 'end', values=(image[0], image[1], loc))

    def refresh_teg(self):
        # Refresh table - all tegs
        tegs_db = db.get_list_tegs()
        self.table_tegs.delete(*self.table_tegs.get_children())
        for teg in tegs_db:
            self.table_tegs.insert('', 'end', values=(teg[0], teg[2]))
        # Clear list of selected tegs
        self.selected_teg_list.delete(0, 'end')

    def refresh_desc(self):
        """Refresh description of selected image"""
        self.desc.delete(1.0, 'end')
        if self.desc_select_image is None:
            self.desc.insert(1.0, "")
        else:
            self.desc.insert(1.0, self.desc_select_image)

    def refresh_teg_image(self):
        """Refresh teg list of selected image"""
        self.teg_list.delete(0, 'end')
        if self.id_select_image is not None:
            data = db.get_image_by_id(self.id_select_image)
            if data[2] is not None:
                tegs = data[2].split(', ')
                for teg in tegs:
                    self.teg_list.insert(END, teg)
            else:
                self.teg_list.delete(0, 'end')

    def main_refresh(self):
        self.refresh_images(db.get_images())
        self.refresh_teg()
        self.root.title("DVP  " + "Search ALL")

    def popup_change_menu(self, event):
        if self.name_select_image is None:
            return None
        self.change_menu.post(event.x_root, event.y_root)

    def open_about(self):
        module_about.WindowSettings(self.root)

    def open_settings(self):
        module_settings.WindowSettings(self.root)

    def open_image(self, event):
        """Open image in file explorer
        or in browser by link
        """
        if self.link_select_image is not None:
            os.startfile(self.link_select_image)
        elif self.dir_select_image is not None and self.dir_select_image != "":
            path = self.dir_select_image
            name = self.name_select_image
            os.startfile(path + '/' + name)


if __name__ == "__main__":
    root = Tk()
    root.title('DVP Images')
    root.geometry('1100x60+200+200')
    window = MainWindow(root)
    root.mainloop()
    if window.thread_load_image is not None:
        window.load_allow = False
        window.thread_load_image.join()
