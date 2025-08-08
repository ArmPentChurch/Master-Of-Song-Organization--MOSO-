import json
from pprint import pprint
import os, datetime, re
from SPOT import DATABASE_FILEPATH, ERGER_DIRECTORY, MAX_SONGS, OUTPUT_FOLDER, PAST_SONGS_FILEPATH

# gets songs fron recentsongs and sorts by last three months
def songCollector(sunday_only=False, ignore_sundays=False, three_month_window=True, search_range=90):
    """Generates a list of all the songs sang. Defaults to the last three months both with var and search range.
        When there is two files both with the same name, the date reader misreads

    #### Args:
    # sunday_only (bool, optional): If you wish to search only Sunday songs. Defaults to False.
        ignore_sundays (bool, optional): If you wish to ignore Sunday songs. Defaults to False.
        three_month_window (bool, optional): If you want a 3 month search window. Defaults to True.
        search_range (int, optional): If you want to search within a specific range of dates.
        Must have three_month_window set to False. Search_range defaults to the three month window.\n

    #### Returns:
        blocked_list: a list containing two sub lists one of songs one for the matching book and another for the filename/date
    """
    from json import load
    current_date = datetime.date.today()

    # Format the date and time
    if three_month_window: search_window = (current_date + datetime.timedelta(days=-90)).strftime('%m.%d.%y') #should really be if range == 90, or just not exist
    else : search_window = (current_date + datetime.timedelta(days=-search_range)).strftime('%m.%d.%y')

    with open(PAST_SONGS_FILEPATH, 'r', encoding='utf-8') as f:
        past_songs = load(f)


    blocked_dict = {}
    past_song:str
    for past_song in past_songs:
        if 'TESTSAVE' not in past_song:
            date = past_song.replace('PORC', '').replace('_', '')
            date = re.findall(r"(.*\d)", date)[0]
            fileDate = date  # saving this for later to be used in list
            # Define the date format
            date_format = "%m.%d.%y"
            # Parse the dates into datetime objects
            date1 = datetime.datetime.strptime(search_window, date_format)
            date2 = datetime.datetime.strptime(date, date_format)
            if date1 < date2:
                if sunday_only:
                    if date2.strftime('%A') == "Sunday":  # if date is 3 month fresh and also sunday
                        blocked_dict[fileDate] = {
                            'songList': past_songs[past_song]['songList'],
                            "basePth": past_songs[past_song]["basePth"],
                        }
                elif ignore_sundays:
                    if date2.strftime('%A') != "Sunday":  # if date is within search window and also not from sunday
                        blocked_dict[fileDate] = {
                            'songList': past_songs[past_song]['songList'],
                            "basePth": past_songs[past_song]["basePth"],
                        }
                else:
                    blocked_dict[fileDate] = {
                        'songList': past_songs[past_song]['songList'],
                        "basePth": past_songs[past_song]["basePth"],
                    }
    return blocked_dict

def past_song_search(data:dict, song_num, fast_method=False) -> list[dict]:
    """
    Search for the occurences of a song inside of a collection of songs otherwise known as a day.

    Parameters:
        data (json): The data to search for the song.
        song_num (str): The number of the song to search for.
        book (str): The book to search for the song in.

    Returns:
        found_dates (list): A list of dictionaries containing the filename/date, basePath, and songList if the song is found, or None if the song is not found.
    """
    if not isinstance(data, dict):
        with open(PAST_SONGS_FILEPATH, 'r', encoding='utf-8') as past_songs:
            data = json.load(past_songs)
    found_dates = []
    metadata:dict
    filename:str
    for filename, metadata in data.items():
        songList = metadata.get("songList", False)
        if songList:
            for songNum in songList:
                if song_num == songNum:
                    found_dates.append({filename:metadata})
                    break
    return found_dates

def songSearch(song_num:str, book = ''):
    """
    Basically a wrapper around past_song_search
    A function that searches for a song based on the song number and book provided.

    Parameters:
        song_num (str): The number of the song to search for.
        book (str): (DEPRICATED) The book to search for the song in.

    Returns:
        dict: A dictionary containing information about the found song if it exists, None otherwise.
    """
    import json
    with open(PAST_SONGS_FILEPATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Define the search function
    result = past_song_search(data, song_num)

    if result:
        return result
    else:
        return None
# print(songSearch('1'))
def songChecker(book: str, songNum: str, three_month_window = True, ignore_sundays = False):
    """
    Checks if a song with the given song number in the specified book, has been sang in the last 3 months.

    Args:
        book (str): DEPRICATED DOES NOTHING
        songNum (str): The number of the song to search for.

    Returns:
        Tuple:
            Bool: True if the song exists, False otherwise.
            Str: The date the song was last sang if it exists.
    """

    if three_month_window and not ignore_sundays:
        blocked_list = songCollector()
    elif not three_month_window:
        blocked_list = songCollector(sunday_only=False, ignore_sundays=True, three_month_window=False, search_range=960) # This is for an overall search for latest date on a song
    if ignore_sundays:
        blocked_list = songCollector(sunday_only=False, ignore_sundays=True)

    date_format = "%m.%d.%y"
    # print(blocked_list)
    song_search_results = past_song_search(data=blocked_list, song_num=songNum)
    date_newest = datetime.datetime.strptime("01.01.70", date_format)
    if song_search_results:
        for entry in song_search_results:
            # entry = {'08.08.25': {'songList': ['312'], 'basePth': '08.2025'}}
            for key, value in entry.items():
                print(key)
                date_compare = datetime.datetime.strptime(key, date_format)
                if date_newest < date_compare:
                    date_newest = date_compare
            return True, date_newest.strftime(date_format)
        # return True, date_newest
    return False

def findPastSongs():  # is for finding new files so as to only go through and add those insted of the whole library, which in the near future will be a headache when it gets bigger
    """Made to discover past songs, follows strict formatting for folder and filenames
    This will make a dict. stored and accessed as a json file. It will store the name of the doc, as well as all
    songs it found in the doc, a basepath where the os path for onedrive can be appended, and it will store the last
    modified date, so when searching for files to update it can ignore certain ones whose modified date has not changed.

    Returns:
        None: Saves a json file.
    """
    blacklist = []  # list of unneeded dirs
    with os.scandir(OUTPUT_FOLDER) as ErgerFolders:
        filePths = []
        for ergfolder in ErgerFolders:
            if ergfolder.name not in blacklist:
                # Circa 4/23/2024
                # returns:
                # C:\Users\Armne\OneDrive\Երգեր\01.2024
                # C:\Users\Armne\OneDrive\Երգեր\02.2024
                # C:\Users\Armne\OneDrive\Երգեր\03.2024
                # C:\Users\Armne\OneDrive\Երգեր\04.2024
                # C:\Users\Armne\OneDrive\Երգեր\2023
                if '.' in ergfolder.name:
                    # must be within current yr, so not in a folder like '2023'
                    # these folders go by the format of Month.Yr
                    # Ex:
                    # 01.2024
                    # 02.2024
                    # 03.2024
                    # 04.2024
                    month_folder = ergfolder.path
                    if os.path.isdir(month_folder): # Make sure its a folder
                        basePth = ergfolder.name
                        # print(basePth)
                        filePths.append([
                            month_folder,
                            basePth
                        ])  # add to a stack(array) for processing later via filePths.pop

                else:
                    # Means its a full year
                    # When the year is done, MOSO automatically moves all the month folders
                    # into a year folder. ex: 2024
                    # This is checking that:
                    if os.path.isdir(ergfolder.path):
                        with os.scandir(ergfolder.path) as fullYrFolder:
                            for months in fullYrFolder:
                                if os.path.isdir(months.path):
                                    if months.name not in blacklist:  # to filter out 01.2023
                                        basePth = ergfolder.name + "/" + months.name
                                        # replaces a lot of datetime calls
                                        filePths.append([
                                            months.path,
                                            basePth
                                        ])

    # begin processing the files
    from json import load, dump
    from WordSongUpdater import getNums
    from datetime import datetime
    from os import stat
    with open(PAST_SONGS_FILEPATH, mode='r', encoding='utf-8') as f:
        past_songs = load(f)

    for filepth, basePth in filePths:
        with os.scandir(filepth) as songFolder:
            for song_file in songFolder:
                if ".docx" in song_file.path:
                    if past_songs.get(song_file.name, None):
                        # lookup file in index, and if none do not run code go to else statement
                        dateModOnFile = datetime.fromtimestamp(past_songs[song_file.name]['dateMod'])
                        currDateMod = datetime.fromtimestamp(stat(song_file.path).st_mtime)

                        # if it exists in the index then do this after setting vars for comparison of dates
                        if not (currDateMod <= dateModOnFile):
                            # if the date modified of a file is greater than the one on file repalce it
                            past_songs[song_file.name] = {
                                'dateMod': stat(song_file.path).st_mtime,
                                'path': song_file.path, # Possibly don't need this as I am already saving the base path, therefore this is a derived value.
                                "basePth": basePth,
                                'songList': getNums(song_file.path, return_list=True)
                            }
                            print("Updated this file", song_file.name)
                    else:
                        past_songs[song_file.name] = {
                            'dateMod': stat(song_file.path).st_mtime,
                            'path': song_file.path,
                            "basePth": basePth,
                            'songList': getNums(song_file.path, return_list=True)
                        }

    # save to json
    with open(PAST_SONGS_FILEPATH, mode='w', encoding='utf-8') as saveFile:
        dump(past_songs, saveFile, indent=4, ensure_ascii=False)

    # print(past_songs)

def clean_up_index():
    """
    Cleans up the index by removing songs that no longer exist in the file system.\n

    This function reads the file at PAST_SONGS_FILEAPTH ('past_songs.json'), which contains a dictionary of song metadata.
    It iterates over each song in the dictionary and checks if the corresponding file exists in the file system.
    If a song file is not found, it is marked for deletion. After identifying all the songs to be deleted,
    the function removes them from the dictionary and writes the updated dictionary back to the PAST_SONGS_FILEPATH.

    """
    with open(PAST_SONGS_FILEPATH, 'r', encoding='utf-8') as f:
        past_songs: dict = json.load(f)
        # find all songs that no longer exist
        items_to_delete = []
        for SongFile in past_songs:
            file_pth = past_songs[SongFile]["path"] # Full filepath to the file.
            try:
                os.stat(file_pth)
            except FileNotFoundError:
                print("Deleting " + file_pth + " from index, because it no longer exists")
                items_to_delete.append(SongFile)
        # delete items
        for item in items_to_delete:
            del past_songs[item]

        with open(PAST_SONGS_FILEPATH, 'w', encoding='utf-8') as f:
            json.dump(past_songs, f, indent=4, ensure_ascii=False)

def databaseBuilder(overwrite=True):  # is for finding new files so as to only go through and add those insted of the whole library, which in the near future will be a headache when it gets bigger
    """Made to discover and add new songs to the database.
    This will make a dict. stored and accessed as a json file. It will store the name of the doc, as well as all
    songs it found in the doc, a basepath where the os path for onedrive can be appended, and it will store the last
    modified date, so when searching for files to update it can ignore certain ones whose modified date has not changed.

    Returns:
        None: Saves a json file.
    """

    blacklist = ['']  # list of unneeded dirs
    allowed_filetypes = ['docx', 'doc']
    with os.scandir(ERGER_DIRECTORY) as ErgerFolders:
        filePths = []
        for erg in ErgerFolders:
            erg_name = erg.name
            erg_filetype = erg_name.split('.')[-1]
            if erg.name not in blacklist and erg_filetype in allowed_filetypes:
                filePths.append(
                    erg.path
                )

    # begin processing the files
    from json import load, dump
    from WordSongUpdater import getNums
    from datetime import datetime
    from os import stat

    if overwrite: allsongs = {}
    else:
        with open(DATABASE_FILEPATH, mode='r', encoding='utf-8') as f:
            allsongs = load(f)

    for filepth in filePths:
        song_file_name:str = os.path.basename(filepth)
        song_num: str = re.findall(r"\d+", song_file_name)[0] # Assumes that the song number is the first set of numbers that appears in the filename
        # with os.scandir(filepth) as song_file:
            # for song_file in songFolder:
        if ".docx" in filepth:
            if allsongs.get(song_file_name, None):
                # lookup file in index, and if none do not run code go to else statement
                dateModOnFile = datetime.fromtimestamp(allsongs[song_file_name]['dateMod'])
                currDateMod = datetime.fromtimestamp(stat(filepth).st_mtime)

                # if it exists in the index then do this after setting vars for comparison of dates
                if not (currDateMod <= dateModOnFile):
                    # if the date modified of a file is greater than the one on file repalce it
                    allsongs[song_num] = {
                        # 'dateMod': stat(filepth).st_mtime,
                        "Title": song_file_name.split('.')[0], # Eg: Աստված իմ.docx --> Աստված իմ
                        "v1": filepth,
                        "latestVersion": filepth,
                        "current_version": "1",
                        "key": "",
                        "speed": "",
                        "style": "",
                        "song_type": "",
                        "timeSig": "",
                        "Comments": "",
                        # 'songList': getNums(song_file.path)
                    }
                    print("Updated this file", song_file_name)
            else:
                allsongs[song_num] = {
                    # 'dateMod': stat(filepth).st_mtime,
                    "Title": song_file_name.split('.')[0],
                    "v1": filepth,
                    "latestVersion": filepth,
                    "current_version": "1", # Easier when recalling info, that everything is a str cmp to having to do logic to parse if string or not
                    "key": "",
                    "speed": "",
                    "style": "",
                    "song_type": "",
                    "timeSig": "",
                    "Comments": "",
                    # 'songList': getNums(song_file.path)
                }
    # Sort the entires by song num
    def sortEntries():
        """Sort the entires by song num
        """
        # Returns sorted keys
        sorted_keys = sorted(allsongs.keys(), key=int)
        # Adding the songs in new sorted order
        new_dict = {}
        for key in sorted_keys:
            new_dict[key] = allsongs[key]
        return new_dict
    allsongs = sortEntries()
    # save to json
    with open(DATABASE_FILEPATH, mode='w', encoding='utf-8') as saveFile:
        dump(allsongs, saveFile, indent=4, ensure_ascii=False)

    # print(allsongs)
def findEmptySongNum(amount_to_generate=1):
   with open(DATABASE_FILEPATH, 'r', encoding='utf-8') as f:
    songs:dict = json.load(f)
    found_nums = []
    for x in range(1,MAX_SONGS):
        if len(found_nums) < amount_to_generate:
            if not songs.get(str(x), None):
                found_nums.append(x)
        else:
            break
    return found_nums

# TODO: Add a function to add new songs,
# Scenario: prog sees a new song, it looks for a empty song num
# Finds none, and starts to add/make new ones incrementing by a factor of one.
if __name__ == '__main__':
    # Uncomment this to manually update the index
    # print(findNewFiles())
    # clean_up_index()
    # print(findEmptySongNum(amount_to_generate=20))
    # print(databaseBuilder())
    # print(findEmptySongNum())
    # findPastSongs()
    # past_song_search("","123")
    # clean_up_index()
    ...