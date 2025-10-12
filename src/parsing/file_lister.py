import os

def list_files(directory, level=0):
    # use the recursion for every folder in each level
    item = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_dir():
                # if is folder, first add its name to item
                item.append((' '*level)+f"[DIR]{entry.name}")
                item.extend(list_files(entry, level+1))
            else:
                # if is a file, direct add its name to item
                item.append((' ' * level) + f"{entry.name}")
    # finish recursion, return item
    return item