import os
import json
import time
from concurrent.futures import ThreadPoolExecutor, thread
# Used for a better input(),
# doesn't even need to be called!
import readline
# Custom scripts
from getAllLyrics import getAllLyrics
from scanningDir import databaseBuilder

def save_config() -> None:
    with open(".moso", 'w', encoding='utf-8') as cfg_file:
        json.dump(moso_config_file, cfg_file, indent=4, ensure_ascii=False)
        cfg_file.flush()
    time.sleep(2) # Wait for config file to save
def open_config() -> dict:
    with open(".moso", 'r', encoding='utf-8') as cfg_file:
        return json.load(cfg_file)
def get_folder_path_from_input(prompt=''):
    while True:
        folder_path = input("Please enter the path to the folder (no spaces, or put it in quotation marks): " if not prompt else prompt).strip().strip("'").strip('"')
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
print("Building all lyrics file...")
# It won't work becuase it reads SPOT from a alrealy initialized python file
# So we need to run it in a subproccess or its own thread
# to compile and read from a newly updated version of the SPOT python file
# th = threading.Thread(target=databaseBuilder)
# th.start()
# th.run()
# th.join()
# th = threading.Thread(target=getAllLyrics)
# th.start()
# th.run()

with ThreadPoolExecutor() as exec:
    database_thread = exec.submit(databaseBuilder)
    getAllLyrics_thread = exec.submit(getAllLyrics)
    database_thread.result()
    getAllLyrics_thread.result()