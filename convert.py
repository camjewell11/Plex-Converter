import os, subprocess, json
from tkinter import filedialog
from tkinter import Tk

def convert_files(directory, extension=".mkv"):
    for dirpath, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extension):
                mkv_file = os.path.join(dirpath, filename)
                mp4_file = os.path.join(dirpath, os.path.splitext(filename)[0] + ".mp4")
                subprocess.call(["HandBrakeCLI", "-i", mkv_file, "-o", mp4_file])
                if os.path.exists(mp4_file):  # Check if the MP4 file was created
                    os.remove(mkv_file)  # Delete the MKV file

def get_directory():
    try:
        with open('last_dir.json', 'r') as f:
            directory = json.load(f)
    except FileNotFoundError:
        directory = None

    root = Tk()
    root.withdraw()  # Hide the main window.
    if directory:
        print(f"Current directory is {directory}. Do you want to change it? (yes/no)")
        if input().lower() == 'yes':
            directory = filedialog.askdirectory()  # Show the "ask directory" dialog.
    else:
        directory = filedialog.askdirectory()  # Show the "ask directory" dialog.

    with open('last_dir.json', 'w') as f:
        json.dump(directory, f)

    return directory

convert_files(get_directory())