"""This is being used as the SPOT file
A SPOT file is the:

Single
Point
Of
Truth

Otherwise known as a place to keep varibales which are meat to be constant ie: unchanging
"""
import json
with open(".moso", 'r', encoding='utf-8') as session_file:
    session_data = json.load(session_file)
    DATABASE_FILEPATH = session_data["database"]
    ERGER_DIRECTORY = session_data["erger_directory"]