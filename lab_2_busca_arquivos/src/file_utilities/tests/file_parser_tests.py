from file_parser import FileParser

def test_file_not_found():
    filename = "blablabla.txt"
    term = "bla"

    parser = FileParser()

    occurences, error = parser.count_occurences_of_term(filename, term)

    if(error):
        print(error)
    else:
        print(occurences)

def test_normal_file_without_occurences():
    filename = "./src/file_parser/testfile.txt"
    term = "test"

    parser = FileParser()

    occurences, error = parser.count_occurences_of_term(filename, term)
    if(error):
        print(error)
    else:
        print(occurences)

def test_normal_file_with_occurences():
    filename = "./src/file_parser/file_with_occurences.txt"
    term = "test"

    parser = FileParser()

    occurences, error = parser.count_occurences_of_term(filename, term)

    if(error):
        print(error)
    else:
        print(occurences)

if __name__ == "__main__":
    test_normal_file_with_occurences()