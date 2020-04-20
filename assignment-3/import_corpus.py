"""Helper functions for third session."""
import json
import os
import re
from nltk.tokenize import wordpunct_tokenize

def import_corpus(corpus_path = 'texts', manifest_file = 'manifest.json'):
    """
    Imports a corpus of texts and prepares them for text analysis.

    params:
        corpus_path: a file path to a folder of .txt files with a .json manifest
        manifest_file: the path of the .json manifest file

    returns:
        novels: a list of dicts, each of which represents a novel
    """

    # Import manifest file
    with open(corpus_path + "/" + manifest_file, 'r') as file:
        manifest = json.load(file)

    # Create list of all files other than the manifest file
    file_list = os.listdir(corpus_path)
    file_list = [file for file in file_list if file != manifest_file]

    # Create useful regular expressions
    header_regex = re.compile(r'\A.+\*{3} {0,2}START OF.{,200}\*{3}', flags = re.DOTALL)
    licence_regex = re.compile(r'\*{3} {0,2}END OF.+', flags = re.DOTALL)

    # Instantiate novel list
    novels = {}

    # Loop over files, import and tokenise novels
    for file_name in file_list:

        # Initialise novel dict
        novel = {}

        # Fetch metadata from manifest
        novel['title'] = manifest[file_name]['title']
        novel['author'] = manifest[file_name]['author']

        # Construct full path
        full_path = corpus_path + '/' + file_name

        # Load text
        with open(full_path, 'r', errors='ignore') as file:
            text = file.read()

        # Extract header, footer
        novel['header'] = header_regex.search(text).group()
        novel['licence'] = licence_regex.search(text).group()

        # Delete header and licence, strip out capital and junk, then add text body to novel dict
        text = header_regex.sub('', text)
        text = licence_regex.sub('', text)
        text = text.lower()
        text = re.sub(r'(?<= )(\W|_)+(?=\w)', '', text) # Strip punctuation from before words
        text = re.sub(r'(?<=(\w))(\W|_)+(?=\w)', ' ', text) # And after
        text = re.sub(r' \d+(th|rd|nd|st|mo|\W+)\b', ' ', text) # Also drop numbers
        novel['body'] = text

        # Tokenise text
        tokens = wordpunct_tokenize(text) # apply tokeniser
        # strip out punctuation, numbers and single-character strings other than 'a','A','i' or 'I':
        tokens = [token for token in tokens if re.match(r'^\w{2,}$|^[aAiI0-9]$', token)]
        novel['tokens'] = tokens

        # Output message
        print(f'{novel["title"]}, by {novel["author"]} successfully imported.')

        # Create short title
        short = re.sub(r'\.txt','',file_name)

        # Add to master dict
        novels[short] = novel

    # Final message:
    unique_authors = set([value["author"] for key,value in novels.items()])
    print(f'\n{len(novels)} novels imported, by {len(unique_authors)} unique authors.')

    return novels
