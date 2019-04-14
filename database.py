import sqlite3
import os
from search import search
from main import PROJECT_DIR

# --------------------------------
# Created by YouKiName
# 02.12.2018
# --------------------------------

# Settings
db_loc = os.path.join(os.path.dirname(__file__), 'images_wt.db')
# Connect to Database
connect = sqlite3.connect(db_loc)
cursor = connect.cursor()
# Create table table1 for adding tegs to images
sql = """create table if not exists table_image 
        (id INTEGER PRIMARY KEY, 
         name text, 
         tegs text, 
         description text, 
         dir text, 
         link text)
      """
cursor.execute(sql)
# Create table all_tegs if not exists
sql = """create table if not exists all_tegs (teg text, description text, count integer)"""
cursor.execute(sql)
# Create table all_folder of not exists
sql = """create table if not exists all_folders (id INTEGER PRIMARY KEY, folder text)"""
cursor.execute(sql)

# ************************************************
# Functions


def get_images_from_dir(direct: str):
    try:
        files = os.listdir(direct)
    except FileNotFoundError:
        print("Folder not found!")
        return []
    images_list = []
    for file in files:
        file_l = file.lower()
        if file_l.endswith('.jpg') or file_l.endswith('.jpeg') or file_l.endswith('.png') or file_l.endswith('.gif'):
            images_list.append(file)
    return images_list


def get_images():
    cursor.execute('SELECT * FROM table_image')
    return cursor.fetchall()


def get_images_without_teg():
    """Return all images from DB(table_image) where tegs are None"""
    cursor.execute("SELECT * FROM table_image WHERE tegs is NULL OR tegs = ''")
    images = cursor.fetchall()
    return images


def get_image_by_id(id: int):
    sql = "SELECT * FROM table_image WHERE id = ?"
    cursor.execute(sql, (id, ))
    return cursor.fetchone()


def get_list_tegs():
    """Get list of all tegs from DB table: all_tegs"""
    sql = 'SELECT * FROM all_tegs'
    cursor.execute(sql)
    return cursor.fetchall()


def get_list_folder():
    """Get list of all folder which was added to DB(all_folders)"""
    sql = "SELECT * FROM all_folders"
    cursor.execute(sql)
    return cursor.fetchall()


def add_folder(direct: str):
    """Add location with images to Database(all_folders)
       Return FALSE if this folder(direct) already added to DB
       and TRUE if not added"""
    sql = "SELECT folder FROM all_folders"
    cursor.execute(sql)
    folders = cursor.fetchall()
    not_exist = True  # Checking: there is such a folder in the array or not

    for folder in folders:
        if folder[0].lower() == direct.lower():
            not_exist = False

    if not_exist:
        sql = "INSERT INTO all_folders(FOLDER) VALUES(?)"
        cursor.execute(sql, (direct, ))
        connect.commit()
    return not_exist


def add_all_image(direct: str):
    """Add ALL images to Database(table_image) from direction
    Take direction of images
    Return list of direction and count of adding images
    """
    images_list = get_images_from_dir(direct)
    count_adding = 0
    for image in images_list:
        cursor.execute('SELECT * FROM table_image WHERE name = ? AND dir = ?', (image, direct))
        if cursor.fetchone() is None:
            sql = "INSERT INTO table_image(name, dir) VALUES(?,?)"
            cursor.execute(sql, (image, direct))
            count_adding += 1
    connect.commit()
    ret_list = (direct, count_adding)
    return ret_list


def add_image_from_dir(dir: str, name: str):
    """Add image to Database(table_image) from direction
    Take direction and name of image
    """
    print("TODO!")


def add_img_from_url(url: str):
    link = url
    name = url.split('/')[-1]
    sql = "INSERT INTO table_image(name, link) VALUES(?,?)"
    cursor.execute(sql, (name, link))
    connect.commit()


def add_teg_to_all(teg: str, desc=''):
    sql = "SELECT * FROM all_tegs WHERE teg = ?"
    cursor.execute(sql, (teg,))
    find_teg = cursor.fetchone()
    if find_teg is None:
        # Add new teg to DB(all_tegs)
        sql = """INSERT INTO all_tegs VALUES(?, ?, ?)"""
        cursor.execute(sql, (teg, desc, 1))
        connect.commit()
    else:
        sql = "UPDATE all_tegs SET count = ? WHERE teg = ?"
        count = find_teg[2]
        count += 1
        cursor.execute(sql, (count, teg))
        connect.commit()


def add_teg_to_image(id: int, tegs):
    """Take string with one teg or with many tegs splited comma"""

    split_tegs = tegs.split(', ')
    sql = """SELECT * FROM table_image WHERE id = ?"""
    cursor.execute(sql, (id,))
    temp_tegs = cursor.fetchone()[2]
    sql = "UPDATE table_image SET tegs = ? WHERE id = ?"
    if temp_tegs is None or temp_tegs == '':
        cursor.execute(sql, [tegs, id])
        # Adding teg to DataBase -> all_tegs
        for split_teg in split_tegs:
            add_teg_to_all(split_teg)
    else:
        for split_teg in split_tegs:
            if not(split_teg in temp_tegs.split(', ')):
                cursor.execute(sql, [str(temp_tegs) + ', ' + split_teg, id])
                # Adding teg to DataBase -> all_tegs
                add_teg_to_all(split_teg)

    connect.commit()


def add_description(id: int, desc: str):
    sql = "UPDATE table_image SET description = ? WHERE id = ?"
    cursor.execute(sql, (desc, id))
    connect.commit()


def change_folder_name(id: int, folder: str):
    # get prev value of folder
    sql = "SELECT * FROM all_folders WHERE id = ?"
    cursor.execute(sql, (id,))
    prev_folder = cursor.fetchone()[1]
    # change in all_image(table_1)
    sql = "UPDATE table_image set dir = ? WHERE dir = ?"
    cursor.execute(sql, (folder, prev_folder))
    connect.commit()
    # change in all_folder
    sql = "UPDATE all_folders set folder = ? WHERE id = ?"
    cursor.execute(sql, (folder, id))
    connect.commit()


def change_name_image(id: int, name: str):
    sql = "UPDATE table_image set name = ? WHERE id = ?"
    cursor.execute(sql, (name, id))
    connect.commit()


def change_link_image(id: int, link: str):
    sql = "UPDATE table_image set link = ? WHERE id = ?"
    cursor.execute(sql, (link, id))
    connect.commit()


def delete_teg_from_image(id: int, teg: str):
    sql = """SELECT * FROM table_image WHERE id = ?"""
    cursor.execute(sql, (id,))
    temp_tegs = cursor.fetchone()[2]
    temp_tegs = temp_tegs.split(', ')
    temp_tegs.remove(teg)
    tegs = ''
    for index in range(len(temp_tegs)):
        if tegs == '':
            tegs = temp_tegs[index]
        else:
            tegs = tegs + ', ' + temp_tegs[index]
    sql = """UPDATE table_image SET tegs = ? WHERE id = ?"""
    cursor.execute(sql, (tegs, id))
    # Update all tegs
    sql = """SELECT * FROM all_tegs WHERE teg = ?"""
    cursor.execute(sql, (teg, ))
    tegs_from_db = cursor.fetchone()
    temp_count = tegs_from_db[2]
    temp_count -= 1
    sql = """UPDATE all_tegs SET count = ? WHERE teg = ?"""
    cursor.execute(sql, (temp_count, teg))
    connect.commit()


def delete_teg_for_all(teg: str):
    # Delete teg from images
    images = search((teg, ))
    for image in images:
        delete_teg_from_image(image[0], teg)

    # Delete teg from table all_tegs(DB)
    sql = "DELETE FROM all_tegs WHERE teg = ?"
    cursor.execute(sql, (teg,))
    connect.commit()


def delete_image(id: int):
    """Delete image from DB(table_image) by 1
       Take id of image"""
    sql = "DELETE FROM table_image WHERE id = ?"
    cursor.execute(sql, (id,))
    connect.commit()


def delete_folder(folder: str, del_images=False):
    count = 0 # Count images from selected folder
    sql = "DELETE FROM all_folders WHERE folder = ?"
    cursor.execute(sql, (folder,))
    if del_images:
        sql = "SELECT * FROM table_image WHERE dir = ?"
        cursor.execute(sql, (folder,))
        count = len(cursor.fetchall())
        sql = "DELETE FROM table_image WHERE dir = ?"
        cursor.execute(sql, (folder,))
        connect.commit()
    connect.commit()
    return count


def clear_teg():
    """Delete tegs from DB(all_tegs) where count = 0
       Return count of deleted tegs"""
    sql = "SELECT * FROM all_tegs WHERE count = 0"
    cursor.execute(sql)
    count = len(cursor.fetchall())

    sql = "DELETE FROM all_tegs WHERE count = 0"
    cursor.execute(sql)
    connect.commit()
    return count
