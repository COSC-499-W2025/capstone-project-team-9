import os

def is_folder(path: str) -> bool:
    """
    This function use path string to check if it is a folder or not.
    """
    isFolder = (
        # os.sep is Operating system-specific path separators
        path.endswith(os.sep) # ends with path separators == folder
        or not
        os.path.splitext(path)[1] # no extension == folder
    )
    return isFolder