import os
import json
import shutil #allows copy and overwrite operations
from subprocess import PIPE, run #lets us run any terminal commands
import sys #to access system-specific parameters and functions

"""
Assumptions:
python -m venv .\.venv\

- data directory contains many files and directories
- you are only interested in the games contaiend in this directory
- each game is stored in a directory that contains the word "game"
- each game directory contains a single .go file that must be compiled before it can be run


Project Steps/Requirements:

- Find all game directories from /data
- Create a new /games directory 
- Copy and remove the "game" suffix of all games into the /games directory
- Create a .json file with the information about the games
- Compile all of the game code 
- Run all of the game code-
"""

GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"] # command to compile go code

def find_all_game_paths(source):
    game_paths = []

    for root, dirs, files in os.walk(source): #walk recursively goes through all directories and subdirectories
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower(): #case insensitive search for "game" in directory name
                full_path = os.path.join(source, directory)
                game_paths.append(full_path)
        break # so it only runs once for the top level directory

    return game_paths

def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)
    return new_names

def create_dir(path):
    if not os.path.exists(path): #check if path exists if not make a directory
        os.makedirs(path)

def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest) #removes entire directory tree (recursively deletes all files and subdirectories)
    shutil.copytree(source, dest) #copies entire directory tree from source to target (recursively copies all files and subdirectories)

def make_json_metadata_file(path, game_dirs):
    data = {"gameNames": game_dirs,
            "numberOfGames": len(game_dirs)
            }
    
    with open(path, "w") as f: # this is a called a context manager / writes and overwrites if file already exists / with auto closes file
        json.dump(data, f, indent=4) # dumps string indent for pretty printing 

def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break # stops at first file found
        break

    if code_file_name is None:
        return

    command = GAME_COMPILE_COMMAND + [code_file_name] # build command with file name
    run_command(command, path)

def run_command(command, path):
        cwd = os.getcwd()
        os.chdir(path) # change working directory to path

        result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True) # runs command in terminal
        #stdout and stdin allow us to capture output and input
        #PIPE allows us to pipe data between processes
        print(result) # print output of command

        os.chdir(cwd) # change back to original working directory ensures we go back to where we started

def main(source, target):
    cwd = os.getcwd() #get current working directory   
    source_path = os.path.join(cwd, source) # always use os.path.join to create paths based on the operating system you're working on
    target_path = os.path.join(cwd, target)

    # Find all game directories
    game_paths = find_all_game_paths(source_path)
    new_game_dirs = get_name_from_paths(game_paths, "_game")
    
    # Create target /games directory
    create_dir(target_path)

    for src, dest in zip(game_paths, new_game_dirs): 
        # zipping allows us to iterate over two lists in parallel it makes a list with tuple pairs based on the index of each element
        dest_path =  os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)

    json_path = os.path.join(target_path, "games_metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)


if __name__ == "__main__": 
    #basically checks if you are running this file directly otherwise if imported it would run all the commands in this script
    args = sys.argv
    print(args)
    if len(args) != 3:
        raise Exception("Please provide the data directory path and the output directory path as arguments.")
    
    source, target = args[1:] # strips name of our python file

    main(source, target)

