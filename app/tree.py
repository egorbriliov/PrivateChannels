import os


def cogs_list():
    """Returned all cogs files"""
    directory = "cogs"
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                str = os.path.join(root, file)
                str = str.replace("\\", ".")
                str = str[:-3]
                py_files.append(str)
    return py_files
