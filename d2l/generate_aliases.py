#!/usr/bin/env python3
import os

# Define the base path for the files
base_path = "/Users/clark/toolkit/d2l/txt_files/"

# List of file prefixes to create aliases for
file_prefixes = ['e', 's']

# Function to generate alias commands
def generate_aliases():
    alias_commands = []
    # Loop through each file prefix and create the alias command
    for prefix in file_prefixes:
        for i in range(1, 11):  # Assuming there are 10 files for each prefix
            # Construct the file name
            file_name = f"{prefix}{i}.txt"
            # Construct the alias command
            alias_command = f"alias {prefix}{i}='pbcopy < {os.path.join(base_path, file_name)}'"
            # Append the command to the list
            alias_commands.append(alias_command)
    return alias_commands

# Main function to print out the alias commands
def main():
    for command in generate_aliases():
        print(command)

if __name__ == "__main__":
    main()
