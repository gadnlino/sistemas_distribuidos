from os.path import isfile

class FileFetcher:
    def get_file(self, filename):
        is_file = isfile(filename)

        if (not is_file):
            return None, 'File does not exist.'
        
        file = open(filename, "r")

        file_str = file.read()

        return file_str, None

class FileParser:

    def __init__(self) -> None:
        self.fetcher = FileFetcher()

    def count_occurences_of_term(self, filename:str, term:str):
        
        file_str, error = self.fetcher.get_file(filename)

        if(error):
            return None, error

        occurrences = file_str.count(term)

        return occurrences, None