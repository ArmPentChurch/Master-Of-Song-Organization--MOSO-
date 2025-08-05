#This file/module serves as a helper for my gui app, otherwise known as MOSO
import os, docx, time, re
import json
from docx.document import Document
from docx.shared import Pt, RGBColor
from SPOT import DATABASE_FILEPATH

month = time.strftime('%m')
year = time.strftime('%y')
fullYear = time.strftime('%Y')
day = time.strftime('%d')

def getDocTextAndIndentation(filePath:str, my_doc):
    """Reads a DOCX file and returns a docx file with the text"""
    # user = os.environ.get("USERNAME")
    doc = docx.Document(filePath)
    first = True # to only run on the first line caught, on a song by song basis
    for p in doc.paragraphs:
        first_line_indent = p.paragraph_format.first_line_indent
        left_indent = p.paragraph_format.left_indent
        right_indent = p.paragraph_format.right_indent
        Placeholder = my_doc.add_paragraph().clear()
        for aWord in p.text:
            if re.match(r"\d+", aWord) or aWord == "(" or aWord == ")":
                run = Placeholder.add_run(aWord)
                run.font.color.rgb = RGBColor(255, 0, 0) # Color for red
            else:
                run = Placeholder.add_run(aWord)
                run.font.color.rgb = RGBColor(0, 0, 0) # Color for white
       
        Placeholder.paragraph_format.space_after = 0
        if first_line_indent is not None:
            Placeholder.paragraph_format.first_line_indent = first_line_indent
        if left_indent is not None:
            Placeholder.paragraph_format.left_indent = left_indent
        if right_indent is not None:
            Placeholder.paragraph_format.right_indent = right_indent
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(22)
        
    return my_doc

def getRandomDoc():
    """Gets a random song template"""
    from random import randint
    from glob import glob
    posible_rand_docs = glob("song_templates//*.docx")
    random_doc_num = randint(0, len(posible_rand_docs))
    return docx.Document(posible_rand_docs[random_doc_num-1])

#parses the data inputed and sends back a python-docx file object
def generateSongFile(songnums:list[str]) -> Document:
    """Parses the data inputed and sends back a python-docx file object

    Args:
        songs (list): A list containing all of the song numbers requested
        book (list): used to denote either 'n'ew or 'o'ld databases
        user (str): a str denoting what pc this is being run on

    Raises:
        Wrong file name: thrown by a checker that checks to see if the filePath matchs with what is found

    Returns:
        docx: a word file containing the requested songs
    """
    my_doc = getRandomDoc()
    
    with open(DATABASE_FILEPATH, 'r', encoding='utf-8') as database_file:
        songs_database = json.load(database_file)
    
    for song in songnums:
        filePath = songs_database[song]["latestVersion"] # Get filepath for the latest version of that song

        #Start song tag
        Placeholder = my_doc.add_paragraph()
        run = Placeholder.add_run("[start:song]")
        run.font.color.rgb = RGBColor(127, 165, 249)

        #Build doc from scratch
        getDocTextAndIndentation(filePath=filePath, my_doc=my_doc)
        # My_doc var is automatically updated via the call

        #End song tag
        Placeholder = my_doc.add_paragraph()
        run = Placeholder.add_run("[end:song]")
        run.font.color.rgb = RGBColor(127, 165, 249)
    
    my_doc.add_page_break()
    
    return my_doc

def getPosibleSongs(songnums:list[str]) -> list:
    """Verifies/validates the existense of the selected songs.

    Args:
        songs (list): A list of song nums
        book (list): A list of matching book names

    Returns:
        list: Returns either the name of the file or a message informing the user that it could not find the file.
    """
    posSongList = []

    with open(DATABASE_FILEPATH, 'r', encoding='utf-8') as database_file:
        songs_database:dict = json.load(database_file)

    for songnum in songnums:
        song_filepath = songs_database[songnum].get('latestVersion', None)
        if song_filepath:
            if os.path.exists(song_filepath):
                posSongList.append(songs_database[songnum]['Title'])
            else:
                posSongList.append(f"Sorry song {songnum} could not be located")            
        else:
            posSongList.append(f"Sorry song {songnum} could not be located")
    return posSongList
