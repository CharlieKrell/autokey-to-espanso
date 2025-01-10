#!/bin/python3
"""
This program is to transfer Autokey abbreviations to espanso.
The json file contains the abbreviation and the text file 
contains the text for expansion
"""

import sys
import os
from pathlib import Path
import json
import random

#def read_options():
def check_directories(args):
    """
    Checks if directories from the passed arguments exist.
    """
    if os.path.isdir(args[0]) and os.path.exists(args[1]):
#        print("Good both are existing paths") 
        return True
    else:
#        print("Invalid paths")
        return False

def find_files_with_extension(file_list,file_extension):
    """
    Finds files with extension, also filters out folder.json 
    because that's a generic file provided by AutoKey
    """
    list_of_specific_files = []
    for filename in file_list:
        if filename.endswith(file_extension) and filename != 'folder.json':
            list_of_specific_files.append(filename)
    return list_of_specific_files

def read_json_files(directory, file_list):
    abbreviation_dict = {}
    for file in file_list:
        filepath = directory + file
        with open(filepath, 'r') as json_file:
            data = json.load(json_file)
        if len(data["abbreviation"]["abbreviations"]) == 1:
            abbreviation_dict[file] = data["abbreviation"]["abbreviations"][0]
        else:
            abbreviation_dict[file] = ''
    return abbreviation_dict

def read_txt_files(directory, file_list):
    text_dict = {}
    for file in file_list:
        filepath = directory + file
        with open(filepath, 'r') as text_file:
            content = text_file.readlines()
            #print(content)
        text_dict[file]=content
    return text_dict


def find_read_files(autokey_directory):
    """]]]]]]]]
    Finds all files within the autokey directory 
    Reads the json and .txt files
    Returns master_file_dict which is a dictionary of lists of the abbreviations
    and a list of the text file lines
    Example
    {'base_name': ['::abbreviation', ['test first line\n', 'test second line\n', 'test third line']]
    """
    file_list = os.listdir(autokey_directory)
    #print(file_list)
    json_file_list = find_files_with_extension(file_list,".json")
    #print(json_file_list)
    txt_file_list = find_files_with_extension(file_list,".txt")
    master_file_dict = {}
    for file in txt_file_list:
        word = file[:-4]
        master_file_dict[word]=[]
    #print(txt_file_list)
    #print(master_file_dict)
    #print(file_list)
    abbreviation_dict = read_json_files(autokey_directory, json_file_list)
    #print(abbreviation_dict)
    text_dict = read_txt_files(autokey_directory, txt_file_list)
    for name in master_file_dict:
        master_file_dict[name] = [abbreviation_dict[name + '.json'], text_dict[name + '.txt'] ]
    return master_file_dict
         
def create_espanso_config(autokeys_to_transfer, espanso_config_dir):
    """
    Creates yml configuration file with random sequence of 5 numbers
    Migrates autokeys_to_tranfer to this file, and has to properly escape
    all backslashes and quotes within the strings.
    """
    random_numbers = ""
    for i in range(5):
        random_numbers+=str(random.randint(1,9))
    espanso_filename = "espanso-" + random_numbers + ".yml"
    espanso_path = espanso_config_dir + espanso_filename
    #print(espanso_path)  
    #print(autokeys_to_transfer)      
    print(f"Writing to {espanso_path}")
    with open(espanso_path, 'w') as espanso_file:
        espanso_file.write("matches:\n")
        for abbreviation in autokeys_to_transfer:
            how_many_lines = len(autokeys_to_transfer[abbreviation][1])
            espanso_file.write(f'''  - trigger: "{autokeys_to_transfer[abbreviation][0]}"\n''')
            espanso_file.write('''    replace: "''')
            if how_many_lines == 1:
                escape_backslashes = autokeys_to_transfer[abbreviation][1][0].replace('\\', '\\\\')
                escape_quotes = escape_backslashes.replace('"', '\\"')
                espanso_file.write(f"""{escape_quotes.rstrip()}"\n""")
            elif how_many_lines == 0:
                print("ERROR NOT CORRECT NUMBER OF TEXT LINES")
                return -1
            else:
                for text_line in autokeys_to_transfer[abbreviation][1][:-1]:
                    escape_backslashes = text_line.replace('\\', '\\\\')
                    escape_quotes = escape_backslashes.replace('"', '\\"')
                    espanso_file.write(f'''{escape_quotes.rstrip()}\\n''')
                escape_backslashes = autokeys_to_transfer[abbreviation][1][-1].replace('\\', '\\\\')
                escape_quotes = escape_backslashes.replace('"', '\\"')
                espanso_file.write(f'''{escape_quotes.rstrip()}"\n''')
    print(f"{espanso_path} created.  Please move it to .config/espanso/match for testing")

def print_help_menu():
    print("Usage: autoKey-to-espanso.py /path/to/AutoKeyDirectory/ /directory/to/save/results/")

def main():
    """
    Calls the functions to print help menu, read options, and
    control flow of program.
    """
    args = sys.argv[1:]
    print(len(args))
    if len(args) < 2:
        print_help_menu()
    elif len(args) != 2 or args[0] == "help" or args[0] == "-h":
        print_help_menu()
    elif not check_directories(args):
        print("Invalid directory")
        print_help_menu()
    else:
        autokeys_to_transfer = find_read_files(args[0])
        create_espanso_config(autokeys_to_transfer, args[1])
    

if __name__ == "__main__":
    main()

