import os, json, shutil, logging
from tkinter import filedialog, Tk

workspace_dir = "workspace"
lastHandbrakecliPath = 'generated/last_handbrakecli.json'
lastDirectoryPath = "generated/last_dir.json"
conversion_file = "generated/conversion.log"
whitelist_file = "generated/whitelist.txt"
todolist_file = "generated/todolist.log"

def get_directory():
    directory = None
    try:
        with open(lastDirectoryPath, 'r') as f:
            directory = json.load(f)
    except FileNotFoundError:
        pass

    root = Tk()
    root.withdraw()  # Hide the main window.
    if directory:
        print(f"Current directory is {directory}. Do you want to change it? (yes/no)")
        user_input = input().lower()
        if user_input == 'yes' or user_input == 'y':
            directory = filedialog.askdirectory()  # Show the "ask directory" dialog.
            if directory:  # If a directory was selected
                with open(lastDirectoryPath, 'w') as f:
                    json.dump(directory, f)
                return directory
    if not directory:  # If no directory was selected or loaded from the file
        directory = filedialog.askdirectory()  # Show the "ask directory" dialog.
        with open(lastDirectoryPath, 'w') as f:
            json.dump(directory, f)

    return directory

def get_handbrakecli_path():
    handbrakecli_path = os.path.join(os.getcwd(), "HandBrakeCLI.exe").replace("\\", "/")
    try:
        with open(lastHandbrakecliPath, 'r') as f:
            handbrakecli_path = json.load(f)
    except FileNotFoundError:
        pass

    root = Tk()
    root.withdraw()  # Hide the main window.
    if handbrakecli_path:
        print(f"Current HandBrakeCLI path is {handbrakecli_path}.")
    else:
        handbrakecli_path = filedialog.askopenfilename(title="Select HandBrakeCLI.exe",
                                                        filetypes=(("exe files", "*.exe"), ("all files", "*.*")))
        if handbrakecli_path:  # If a file was selected
            with open(lastHandbrakecliPath, 'w') as f:
                json.dump(handbrakecli_path, f)

    return handbrakecli_path

def clean_workspace(workspace_dir):
    try:
        for filename in os.listdir(workspace_dir):
            file_path = os.path.join(workspace_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logging.error(f"Failed to delete {file_path}. Reason: {e}")
    except Exception as e:
        logging.error(f"Failed to clean workspace {workspace_dir}. Reason: {e}")