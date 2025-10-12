import os

def list_files(path, level=0):
    """
        Recursively lists all files and folders under the specified path (in nested order)
        :param path: start directory
        :param level: Current level (for indentation display)
        :return: A list of strings containing the name of each file/folder
        """
    item = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                # if is folder, first add its name to item
                item.append((' '*level)+f"[DIR] {entry.name}")
                # recursion the sub folders
                item.extend(list_files(entry, level+1))
            else:
                # if is a file, direct add its name to item
                item.append((' ' * level) + f"{entry.name}")
    # finish recursion, return item
    return item