import os
import re, time, docx, json
from turtle import title
from os import path as pth, remove, environ
from docx.document import Document
from docx.shared import Pt
from utils.getAllLyrics import updateSongLyrics
from SPOT import DATABASE_FILEPATH, ERGER_DIRECTORY

month = time.strftime('%m')
year = time.strftime('%y')
fullYear = time.strftime('%Y')
day = time.strftime('%d')

def getLatestVersion(Ergaran_Index:dict[str, dict], songnum:str) -> tuple[int, str]:
    """Finds latest version of given songNum & the song title in given json index & returns it,
    if it can't find it
    The algo will create a empty directory with that song number, and empty values

    Args:
        Ergaran_Index (dict): The dict containing all songs
        songnum (str): The number of the song

    Returns: tuple[str, str]: Containing the current song version and the title
    """
    if Ergaran_Index.get(songnum, False):
        current_version = Ergaran_Index[songnum]["current_version"]
        title = Ergaran_Index[songnum]['Title']
        return (int(current_version), title)
    else:
        current_version = "0"
        title = ""
        Ergaran_Index[songnum] = {
            "Title": title,
            "v1": "",
            "latestVersion": "",
            "current_version": current_version,
            "key": "",
            "speed": "",
            "style": "",
            "song_type": "",
            "timeSig": "",
            "Comments": ""
            }
        return (int(current_version), title)

def getDocTextAndIndentation(filename:str):
    """
    Reads a Word document file and extracts the text and indentation information
    from each paragraph. It identifies song sections based on specific start and
    end indicators in the text and processes the paragraphs accordingly. Then it saves the file.

    Parameters:
        filename (str): The path to the Word document file to be read.

    Returns:
        A list of dictionaries containing the text and indentation information
        for each paragraph in the song sections.
    """

    doc = docx.Document(filename)


    text_and_indentation = [] #turn into a list of dicts
    song = [] # Remove this it does nothing.
    first = True
    have_we_started = False
    for p in doc.paragraphs:

        if "[start:song" in p.text:
            my_doc = docx.Document()
            song = []
            songNum = None
            first = True
            have_we_started = True

            #have to add bc the songNum gets shoved in with the start indicator sometimes: '[start:song]\n171'
            if (re.search(r"[0-9]",p.text)):
                songNum = re.sub(r"\D", "", p.text)
                first = False

        if not("end" in p.text or "start" in p.text) and have_we_started == True:
            if first:
                songNum = p.text.split("\n")[0]
                first=False
            first_line_indent = p.paragraph_format.first_line_indent
            left_indent = p.paragraph_format.left_indent
            right_indent = p.paragraph_format.right_indent

            Placeholder = my_doc.add_paragraph(p.text) # type: ignore
            Placeholder.paragraph_format.space_after = 0
            if first_line_indent is not None:
                Placeholder.paragraph_format.first_line_indent = first_line_indent
            if left_indent is not None:
                Placeholder.paragraph_format.left_indent = left_indent
            if right_indent is not None:
                Placeholder.paragraph_format.right_indent = right_indent

            song.append({
                'text': p.text,
                'first_line_indent': first_line_indent,
                'left_indent': left_indent,
                'right_indent': right_indent
            })
        if "end" in p.text: # Def ending loc
            if doc.paragraphs[1].text:
                saveDocFromDoc(my_doc, songNum) # type: ignore
            else:
                print("No Pass!")
            #push song to text var and reset song var
            bookOld = False
            song = []

def saveDocFromDoc(song_Doc: Document, songNum:str):
    """Saves an individual song, sent from getDocTextAndIndentation

    method logic:
        1. check if song exists in relevant book/index
        2. if so, append to index, "version", and "latestVersion"
        2.1 Based on this info the program needs to generate a suitable filepath to be logged and saved.
        2.5 if not, append to index, "SongNum", "Title", "version", and "latestVersion"
        3. once the lv(LatestVersion) is acquired, then add one and get new var cv(Current Version)
        4. Given the cv now create file path and amend to json index
        4.5 Save at the newly created file path
        4.7 If tues/thurs no need to save
    Args:
        song_Doc (docx): A docx object. That contains an individual song.
        oldBook (bool): Boolean value for if its from the old book
        songNum (str): A song number stored in a string, how funny ;)
    """

    # Possibly add a check where it checks to see if any songs have the same title and updates with the latest ie: song '3' and '3 ' should be combined so as to not cause later confusion
    if songNum == None:
        return

    with open(DATABASE_FILEPATH, "r", encoding='utf-8') as f:
        Ergaran_Index = json.load(f)

    current_version, title = getLatestVersion(Ergaran_Index=Ergaran_Index, songnum=songNum)#add 1 to get the current version
    current_version += 1
    print(Ergaran_Index[songNum])
    # print("Debug String..")  # Note: Funny enough the test num I used does not have a corresponding title, which does not really matter that much, however I could add some functionality to fill it later on
    # However I'm not so sure about just saving files in ergaran as songnum.docx like I already do in red ergaran
    clean_title = title.split('\n')[0]
    file_path = f"{ERGER_DIRECTORY}/{songNum} {clean_title} v{current_version}"
    Ergaran_Index[songNum]["v"+ str(current_version)] = file_path
    Ergaran_Index[songNum]["latestVersion"] = file_path
    Ergaran_Index[songNum]["current_version"] = current_version
    style = song_Doc.styles['Normal']
    font = style.font # type: ignore
    font.name = 'Arial'
    font.size = Pt(22)
    song_Doc.save(os.path.join(DATABASE_FILEPATH, file_path))
    with open(DATABASE_FILEPATH, 'w', encoding='utf-8') as f:
        #Book_Index["SongNum"] = dict(sorted(Book_Index["SongNum"].items(), key=lambda x: int(x[0]))) # should sort the songs before saving
        json.dump(Ergaran_Index, f, indent=4, ensure_ascii=False)
    print(file_path)

    if not False:
        # TODO: Update!
        if updateSongLyrics(book="new", songNum=songNum, lyrics = song_Doc) == None:
            print("Lyrics not Updated")
            print(f"Song Num: {songNum} Book: New")
        else:
            print("Lyrics Updated")
    # else:
    #     if updateSongLyrics(book="old", songNum=songNum, lyrics = song_Doc) == None:
    #         print("Lyrics not Updated")
    #         print(f"Song Num: {songNum} Book: New")
    #     else:
    #         print("Lyrics Updated")

def getNums(filename: str, return_list=False):
    """Reads the file and returns a dict with the text along with a bool if it is from the old book"""
    doc = docx.Document(filename)
    SongList = []
    first = True
    songNum = None
    for p in doc.paragraphs:
        if "[start:song" in p.text:
            songNum = None
            first = True

            #have to add bc the songNum gets shoved in with the start indicator sometimes: '[start:song]\n171'
            if (re.search(r"[0-9]",p.text)):
                songNum = re.sub(r"\D", "", p.text)
                first = False

        if not("end" in p.text or "start" in p.text):
            if first:
                songNum = p.text.split("\n")[0]
                first=False

        if "end" in p.text:  # Def ending loc
            SongList.append(songNum)

    # return text_and_indentation
    if return_list: return SongList
    else: return str(SongList)

if "__main__" == __name__:
    # print(getDocTextAndIndentation(r"C:\Users\moses\OneDrive\Երգեր\10.2024\10.31.24TESTSAVE.docx"))
    song_nums = getNums(r"C:\Users\moses\OneDrive\Երգեր\07.2025\07.27.25.docx", return_list=True)