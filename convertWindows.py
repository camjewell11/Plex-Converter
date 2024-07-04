import os, subprocess, json, logging, shutil
from tkinter import filedialog, Tk

lastDirectoryPath = 'last_dir.json'
lastHandbrakecliPath = 'last_handbrakecli.json'
workspace_dir = "workspace"

# Set up logging
logging.basicConfig(filename='conversion.log', level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

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

def process_file_with_workspace(source_file_path, destination_file_path, command):
    workspace_dir = "workspace"
    os.makedirs(workspace_dir, exist_ok=True)  # Ensure the workspace directory exists

    # Define workspace paths
    workspace_source_path = os.path.join(workspace_dir, os.path.basename(source_file_path))
    workspace_destination_path = os.path.join(workspace_dir, os.path.basename(destination_file_path))

    try:
        print(f"Copying source file to workspace: {source_file_path} -> {workspace_source_path}")
        logging.info(f"Copying source file to workspace: {source_file_path} -> {workspace_source_path}")
        # Copy source file to workspace
        shutil.copy2(source_file_path, workspace_source_path)

        # Update command to use workspace paths
        command = [arg.replace(source_file_path, workspace_source_path).replace(destination_file_path, workspace_destination_path) for arg in command]

        # Execute the conversion command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline, b''):
            line = line.decode()
            if "Encoding: " in line:
                print(line, end='')

        # Ensure the subprocess has completed
        process.wait()

        print(f"Copying converted file back to original location: {workspace_destination_path} -> {destination_file_path}")
        logging.info(f"Copying converted file back to original location: {workspace_destination_path} -> {destination_file_path}")

        # Copy the converted file back to its original location
        shutil.copy2(workspace_destination_path, destination_file_path)
    except Exception as e:
        print(f"An error occurred during the file processing: {e}")
        logging.error(f"An error occurred during the file processing: {e}")
        clean_workspace(workspace_dir)
    finally:
        # Clean up the workspace
        try:
            if os.path.exists(workspace_source_path):
                os.remove(workspace_source_path)
            if os.path.exists(workspace_destination_path):
                os.remove(workspace_destination_path)
        except Exception as e:
            logging.error(f"Failed to clean up workspace: {e}")

def convert_files(directory, extension=".mkv"):
    handbrakecli_path = get_handbrakecli_path()
    try:
        with open('whitelist.txt', 'r') as f:
            whitelist = set(f.read().splitlines())
    except FileNotFoundError:
        whitelist = set()

    for dirpath, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith(extension) and filename not in whitelist:
                mkv_file = os.path.join(dirpath, filename).replace("\\", "/")
                mp4_file = os.path.join(dirpath, os.path.splitext(filename)[0] + ".mp4").replace("\\", "/")
                command = [handbrakecli_path, "-i", mkv_file, "-o", mp4_file, "--encoder", "nvenc_h264", "--quality", "20.0"]
                print(f"\nStarting conversion of {filename}")
                logging.info(f"Starting conversion of {filename}")

                process_file_with_workspace(mkv_file, mp4_file, command)

                print(f"\nFinished conversion of {filename}")
                logging.info(f"Finished conversion of {filename}")
                if os.path.exists(mp4_file):  # Check if the MP4 file was created
                    os.remove(mkv_file)  # Delete the MKV file
            elif filename in whitelist:
                print(f"Skipping {filename}")
                logging.info(f"Skipping {filename}")

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

clean_workspace(workspace_dir)
root = Tk()
root.withdraw()  # Hide the main window.
convert_files(get_directory())