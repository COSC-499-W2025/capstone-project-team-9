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
        for entry in sorted(entries, key=lambda e: e.name):
            if entry.is_dir():
                item.append(('  ' * level) + f"[DIR] {entry.name}")
                item.extend(list_files(entry.path, level + 1))
            else:
                item.append(('  ' * level) + f"{entry.name}")
    return item