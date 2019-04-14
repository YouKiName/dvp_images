import database as db

# --------------------------------
# Created by YouKiName
# 02.12.2018
# --------------------------------


def search(tegs: list):
    """Take list of tegs for search
    Return list of images with given tegs
    """
    images = db.get_images()
    if not tegs or tegs[0] == '' or tegs is None:
        return images
    for teg in tegs:
        temp_images = []
        for j in range(len(images)):
            try:
                tegs = images[j][2]
                tegs = tegs.split(', ')
            except AttributeError:
                continue
            except Exception:
                print('Damned... Exception - def search')
                continue
            if teg in tegs:
                temp_images.append(images[j])

        images = temp_images

    return images


def advanced_search(tegs: list):
    """Search in tegs or teg's parts, in description
    Take list of tegs for search
    Return list of images which passed search
    """
    images = db.get_images()
    if not tegs or tegs[0] == '' or tegs is None:
        return db.get_images_without_teg()

    for teg in tegs:
        temp_images = []
        for j in range(len(images)):
            try:
                tegs = images[j][2].lower()
            except AttributeError:
                tegs = ""
            try:
                desc = images[j][3].lower()
            except AttributeError:
                desc = ""
            if teg.lower() in tegs or teg.lower() in desc:
                temp_images.append(images[j])

        images = temp_images

    return images
