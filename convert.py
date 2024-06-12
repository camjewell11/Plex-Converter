import os, subprocess, json
from tkinter import filedialog, Tk

def convert_files(directory, extension=".mkv", handbrakecli_path="HandBrakeCLI"):
    for dirpath, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extension):
                mkv_file = os.path.join(dirpath, filename)
                mp4_file = os.path.join(dirpath, os.path.splitext(filename)[0] + ".mp4")
                call_handbrake(mkv_file=mkv_file, mp4_file=mp4_file, handbrakecli_path=handbrakecli_path)
                if os.path.exists(mp4_file):  # Check if the MP4 file was created
                    os.remove(mkv_file)  # Delete the MKV file

def call_handbrake(mkv_file, mp4_file, handbrakecli_path="HandBrakeCLI"):
    try:
        subprocess.call([handbrakecli_path, "-i", mkv_file, "-o", mp4_file])
    except FileNotFoundError:
        root = Tk()
        root.withdraw()  # Hide the main window.
        handbrakecli_path = filedialog.askopenfilename(title="Select HandBrakeCLI.exe",
                                                        filetypes=(("exe files", "*.exe"), ("all files", "*.*")))
        if handbrakecli_path:  # If a file was selected
            subprocess.call([handbrakecli_path, "-i", mkv_file, "-o", mp4_file])

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
        if input().lower() == 'yes' or input().lower() == 'y':
            directory = filedialog.askdirectory()  # Show the "ask directory" dialog.
    else:
        directory = filedialog.askdirectory()  # Show the "ask directory" dialog.

    with open('last_dir.json', 'w') as f:
        json.dump(directory, f)

    return directory

convert_files(get_directory())