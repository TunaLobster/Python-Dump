import os

import xlsxwriter
from fuzzywuzzy import fuzz


# TODO: I should probably write a generator for files that have the correct extension
# TODO: Write this to handle filenames without numbers
def filename_parser(filename: str):
    number, name, date, submission = filename.split(' - ', 3)
    lastname, firstname = name.split(' ', 1)
    return [number, lastname, firstname, date, submission]


def split_filenames(path: str, exts: list):
    """

    :param path: Directory sting where the submitted assignments were downloaded and extracted to
    :param exts: Tuple of stings of file extensions to scan for. Example: ('.py') or ('.sldprt','.sldasm')
    :return:
    """
    allfiles = os.listdir(path)
    data = [['number', 'lastname', 'firstname', 'data', 'filename submitted']]
    for filename in allfiles:
        for ext in exts:
            if not filename.lower().endswith(ext.lower()):
                continue
            # number, name, date, submission = filename.split(' - ', 3)
            # lastname, firstname = name.split(' ', 1)
            # data.append([number, lastname, firstname, date, submission])
            data.append(filename_parser(filename))
    return data


# TODO: Handle case of numbers not at start of files (regex)
def remove_numbers(path: str, exts: list):
    allfiles = os.listdir(path)
    for filename in allfiles:
        for ext in exts:
            if not filename.lower().endswith(ext.lower()):
                continue
            os.rename(os.path.join(path, filename), os.path.join(path, filename[filename.find(' - ') + 3:]))


def remove_everything(path: str, exts: list):
    while True:
        try:
            allfiles = os.listdir(path)
            for filename in allfiles:
                for ext in exts:
                    if not filename.lower().endswith(ext.lower()):
                        continue
                    if filename.find(' - ') == -1:
                        continue
                    s1 = filename.find(' - ') + 3
                    s2 = filename.find(' - ', s1) + 3
                    os.rename(os.path.join(path, filename), os.path.join(path, filename[filename.find(' - ', s2) + 3:]))
        # Handle multiple files being submitted with the same name
        except FileExistsError as e:
            if os.path.getmtime(e.filename) > os.path.getmtime(e.filename2):
                os.remove(e.filename2)
            else:
                os.remove(e.filename)
            continue
        break


def write_to_excel(path: str, data: list, outputfilename: str):
    # note that xlsxwriter cannot overwrite existing files
    if not outputfilename.lower().endswith('.xlsx'):
        outputfilename = '.'.join([outputfilename, 'xlsx'])
    workbook = xlsxwriter.Workbook(os.path.join(path, outputfilename))
    worksheet = workbook.add_worksheet()
    for row in range(len(data)):
        for col in range(len(data[row])):
            worksheet.write(row, col, data[row][col])
    workbook.close()


def scan_for_soltuions(path: str, exts: list, percent: int):
    # external file with a list of solutions copied and pasted from the internet in a python list.
    # Example "solutions.py" file contents:
    # solutionlist = ['''copied from google result''','''students shouldn't do this''','''so many ways to tell''']
    import solutions
    solutionslist = solutions.solutionlist
    allfiles = os.listdir(path)
    for filename in allfiles:
        for ext in exts:
            if not filename.lower().endswith(ext.lower()):
                continue
            with open(os.path.join(path, filename), 'r', encoding='UTF-8') as studentfile:
                studentcode = studentfile.read()
            for soltuion in solutionslist:
                # token set ratio had best results
                score = fuzz.token_set_ratio(soltuion, studentcode)
                if score > percent:
                    yield filename_parser(filename)[1:3], filename_parser(filename)[-1], score


# DONE: Add function to compare students. Should be bigO(1/n)?
def scan_for_copying(path: str, exts: list, percent: int):
    allfiles = os.listdir(path)
    for ext in exts:
        for i in range(len(allfiles) - 1):
            if not allfiles[i].lower().endswith(ext.lower()):
                continue
            with open(os.path.join(path, allfiles[i]), 'r', encoding='UTF-8') as checkfile:
                checkcode = checkfile.read()
                for filename in allfiles[i + 1:]:
                    if not filename.lower().endswith(ext.lower()):
                        continue
                    with open(os.path.join(path, filename), 'r', encoding='UTF-8') as studentfile:
                        studentcode = studentfile.read()
                        score = fuzz.ratio(checkcode, studentcode)
                        # lets ignore some files to speed it up some.
                        # if score >= 98:
                        #     continue
                        # ignoring instructor supplied modules
                        # if filename.find(r'OpenGL_2D_class.py') != -1 or allfiles[i].find(r'OpenGL_2D_class.py') != -1:
                        #     continue
                        if filename_parser(filename)[1:3] == filename_parser(allfiles[i])[1:3]:
                            continue
                        if score >= percent:
                            yield filename_parser(filename)[1:3], filename_parser(filename)[-1], score, \
                                  filename_parser(allfiles[i])[1:3], filename_parser(allfiles[i])[-1]


def __example__():
    path = r'C:\Users\Charlie\Dropbox\Graduate\GTA\3403S19\Grading\Final Project - one zip file per team Download May 10, 2019 156 PM'
    extensions = ['.py', '.zip', '.rar', '.7z']
    outputfilename = '3403S19 Final Project grades'
    percentsimilar = 95
    # 85 seemed to turn up the most likely candidates for copying solutions.
    # 95 seemed to work well for finding students copying each other.

    studentfilenamedata = split_filenames(path, extensions)
    write_to_excel(path, studentfilenamedata, outputfilename)

    # only really useful when the submissions are code or text files
    copiesfound = scan_for_copying(path, ['.py'], percentsimilar)
    for i in copiesfound:
        print(i)
    # solutionsfound = scanforsoltuions(path, extensions, percentsimilar)
    # for i in solutionsfound:
    #     print(i)

    # DO THIS LAST (For now at least. I'll fix it later.)
    remove_numbers(path, extensions)
    # remove_everything(path, extensions)


# TODO: Objectify the whole thing
if __name__ == '__main__':
    __example__()
