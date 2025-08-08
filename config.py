import os
import json
import time
# Used for a better input(),
# doesn't even need to be called!
import readline

from getAllLyrics import getAllLyrics
from scanningDir import databaseBuilder

def save_config() -> None:
    cfg_file = open(".moso", 'w', encoding='utf-8')
    json.dump(moso_config_file, cfg_file, indent=4, ensure_ascii=False)
    cfg_file.flush()
    cfg_file.close()
#     with open(".moso", 'w', encoding='utf-8') as cfg_file:
#         json.dump(moso_config_file, cfg_file, indent=4, ensure_ascii=False)
#         cfg_file.flush()
def open_config() -> dict:
    with open(".moso", 'r', encoding='utf-8') as cfg_file:
        return json.load(cfg_file)
def get_folder_path_from_input(prompt=''):
    while True:
        folder_path = input("Please enter the path to the folder (no spaces, or put it in quotation marks): " if not prompt else prompt).strip("'").strip('"')
        if os.name == 'posix':
            folder_path = folder_path.strip("\\")
        if os.path.isdir(folder_path):
            return folder_path
        else:
            print("Invalid path. The specified folder does not exist. Please try again.")
def config_process() -> tuple[str, str]:
    print("Beginning the configuration process...")
    erger_directory = get_folder_path_from_input("Please enter the path to the folder containing all song files (no spaces, or put it in quotation marks): ")
    output_folder = get_folder_path_from_input("Please enter the path to the folder where you want the songs to be outputed (no spaces, or put it in quotation marks): ")
    # print(f"You selected the folder: {selected_folder}")
    print("Please look at the inputed directories and confirm if its correct, otherwise restart the process.")
    print(f"For the folder containing all your songs, you choose: {erger_directory}")
    print(f"For the output folder you choose: {output_folder}")
    answer = input("Is this correct? Yes or No: ")
    if answer.lower() == 'no' or answer.lower() == 'n':
        return config_process()
    else:
        return (erger_directory, output_folder)
erger_directory, output_folder = config_process()
moso_config_file = open_config()
moso_config_file["erger_directory"] = erger_directory
moso_config_file["output_folder"] = output_folder
save_config()
print("Config files updated successfully!")
print("Building database...")
time.sleep(0.5) # Wait for config file to save
databaseBuilder()
print("Building all lyrics file...")
getAllLyrics()