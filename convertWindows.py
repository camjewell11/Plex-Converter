import os, subprocess, json
from tkinter import filedialog, Tk

lastDirectoryPath = 'last_dir.json'
lastHandbrakecliPath = 'last_handbrakecli.json'

def convert_files(directory, extension=".mkv"):
    handbrakecli_path = get_handbrakecli_path()
    for dirpath, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extension):
                mkv_file = os.path.join(dirpath, filename).replace("\\", "/")
                mp4_file = os.path.join(dirpath, os.path.splitext(filename)[0] + ".mp4").replace("\\", "/")
                command = [handbrakecli_path, "-i", mkv_file, "-o", mp4_file]
                print(f"\nStarting conversion of {filename}")
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in iter(process.stdout.readline, b''):
                    line = line.decode()
                    if "Encoding: " in line:
                        print(line, end='')
                print(f"\nFinished conversion of {filename}")

def get_handbrakecli_path():
    # os.path.join(os.getcwd(), "HandBrakeCLI.exe").replace("\\", "/")
    handbrakecli_path = None
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

root = Tk()
root.withdraw()  # Hide the main window.
convert_files(get_directory())