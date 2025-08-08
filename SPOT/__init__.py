"""This is being used as the SPOT file
A SPOT file is the:

Single
Point
Of
Truth

Otherwise known as a place to keep varibales which are meat to be constant ie: unchanging
"""
from json import load
with open(".moso", 'r', encoding='utf-8') as session_file:
    session_data = load(session_file)
    DATABASE_FILEPATH:str = session_data["database"]
    ERGER_DIRECTORY:str = session_data["erger_directory"]
    OUTPUT_FOLDER:str =  session_data["output_folder"]
    PAST_SONGS_FILEPATH:str = session_data["past_songs"]
    ALL_LYRICS:str = session_data["all_lyrics"]
    MAX_SONGS:int = session_data["max_songs"]

import warnings
from functools import wraps

def incomplete(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(f"{func.__name__} is incomplete - use at your own risk",
                     UserWarning, stacklevel=2)
        return func(*args, **kwargs)
    return wrapper