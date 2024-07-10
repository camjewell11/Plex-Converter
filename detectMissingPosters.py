import os
from utilities import get_directory

def contains_poster_file(directory, poster_name_pattern="poster.jpg"):
    for entry in os.listdir(directory):
        if entry == poster_name_pattern:
            return True
    return False

def find_directories_without_posters(root_directory):
    directories_without_posters = []
    for dirpath, dirnames, filenames in os.walk(root_directory):
        if not contains_poster_file(dirpath):
            directories_without_posters.append(dirpath)
    return directories_without_posters

# Specify the root directory to start the search from
plex_directory = get_directory()

# Find directories without poster files
missing_posters = find_directories_without_posters(plex_directory)

# Print the list of directories without poster files to a file
with open("missingPosters.txt", 'w') as file:
    for directory in missing_posters:
        file.write(directory + '\n')