import os, subprocess, logging, shutil
from tkinter import Tk
from utilities import clean_workspace, get_directory, get_handbrakecli_path, conversion_file, workspace_dir, todolist_file, whitelist_file

# Set up logging
logging.basicConfig(filename=conversion_file, level=logging.INFO,
                    format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def process_file_with_workspace(source_file_path, destination_file_path, command):
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

def log_mkv_files(directory):
    with open(todolist_file, 'w') as log_file:
        for dirpath, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.mkv'):
                    mkv_file_path = os.path.join(dirpath, filename).replace("\\", "/")
                    log_file.write(mkv_file_path + '\n')
                    print(f"Logged {filename}")

def convert_files(directory, extension=".mkv"):
    handbrakecli_path = get_handbrakecli_path()
    try:
        with open(whitelist_file, 'r') as f:
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

clean_workspace(workspace_dir)
plex_directory = get_directory()
log_mkv_files(plex_directory)
root = Tk()
root.withdraw()
convert_files(plex_directory)