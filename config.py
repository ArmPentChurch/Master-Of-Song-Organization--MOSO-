import os
import json

# Used for a better input(),
# doesn't even need to be called!
import readline

def save_config() -> None:
    with open(".moso", 'w', encoding='utf-8') as cfg_file:
        json.dump(moso_config_file, cfg_file, indent=4, ensure_ascii=False)
def open_config() -> dict:
    with open(".moso", 'r', encoding='utf-8') as cfg_file:
        return json.load(cfg_file)
def get_folder_path_from_input(prompt=''):
    while True:
        folder_path = input("Please enter the path to the folder: " if not prompt else prompt).strip("'").strip('"')
        if os.path.isdir(folder_path):
            return folder_path
        else:
            print("Invalid path. The specified folder does not exist. Please try again.")
def config_process() -> tuple[str, str]:
    print("Beginning the configuration process...")
    erger_directory = get_folder_path_from_input("Please enter the path to the folder containing all song files: ")
    output_folder = get_folder_path_from_input("Please enter the path to the folder where you want the sogns to be outputed: ")
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