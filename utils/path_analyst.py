import os

def is_folder(path: str) -> bool:
    """
    This function use path string to check if it is a folder or not.
    """
    isFolder = (
        # os.sep is Operating system-specific path separators
        path.endswith(os.sep) # Determine if the path ends with path separators
        or not
        os.path.split(path)[1] # if path not end with extend name, it consider as folder
    )
    return isFolder