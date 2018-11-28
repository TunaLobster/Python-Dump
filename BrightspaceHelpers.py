import os

import xlsxwriter
from fuzzywuzzy import fuzz


# TODO: I should probably write a generator for files that have the correct extension
# TODO: Write this to handle filenames without numbers
def filenameparser(filename: str):
    number, name, date, submission = filename.split(' - ', 3)
    lastname, firstname = name.split(' ', 1)
    return [number, lastname, firstname, date, submission]


def splitfilenames(path: str, exts: list):
    """

    :param path: Directory sting where the submitted assignments were downloaded and extracted to
    :param ext: Tuple of stings of file extensions to scan for. Example: ('.py') or ('.sldprt','.sldasm')
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
            data.append(filenameparser(filename))
    return data


# TODO: Handle case of numbers not at start of files
# TODO: Change to using the filename parser function
def removenumbers(path: str, exts: list):
    allfiles = os.listdir(path)
    for filename in allfiles:
        for ext in exts:
            if not filename.lower().endswith(ext.lower()):
                continue
            os.rename(os.path.join(path, filename), os.path.join(path, filename[filename.find(' - ') + 3:]))


def write2excel(path: str, data: list, outputfilename: str):
    # note that xlsxwriter cannot overwrite existing files
    if not outputfilename.lower().endswith('.xlsx'):
        outputfilename = '.'.join([outputfilename, 'xlsx'])
    workbook = xlsxwriter.Workbook(os.path.join(path, outputfilename))
    worksheet = workbook.add_worksheet()
    for row in range(len(data)):
        for col in range(len(data[row])):
            worksheet.write(row, col, data[row][col])
    workbook.close()


def scanforsoltuions(path: str, exts: list, percent: int):
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
            with open(os.path.join(path, filename), 'r') as studentfile:
                studentcode = studentfile.read()
            for soltuion in solutionslist:
                # token set ratio had best results
                score = fuzz.token_set_ratio(soltuion, studentcode)
                if score > percent:
                    yield filenameparser(filename)[1:3], filenameparser(filename)[-1], score


# DONE: Add function to compare students. Should be bigO(1/n)?
def scanforcopying(path: str, exts: list, percent: int):
    allfiles = os.listdir(path)
    for ext in exts:
        for i in range(len(allfiles) - 1):
            if not allfiles[i].lower().endswith(ext.lower()):
                continue
            with open(os.path.join(path, allfiles[i]), 'r') as checkfile:
                checkcode = checkfile.read()
                for filename in allfiles[i + 1:]:
                    if not filename.lower().endswith(ext.lower()):
                        continue
                    with open(os.path.join(path, filename), 'r') as studentfile:
                        studentcode = studentfile.read()
                        score = fuzz.ratio(checkcode, studentcode)
                        # lets ignore some files to speed it up some.
                        # if score >= 98:
                        #     continue
                        # ignoring instructor supplied modules
                        # if filename.find(r'OpenGL_2D_class.py') != -1 or allfiles[i].find(r'OpenGL_2D_class.py') != -1:
                        #     continue
                        if filenameparser(filename)[1:3] == filenameparser(allfiles[i])[1:3]:
                            continue
                        if score >= percent:
                            yield filenameparser(filename)[1:3], filenameparser(filename)[-1], score, filenameparser(
                                allfiles[i])[1:3], filenameparser(allfiles[i])[-1]


def __example__():
    path = r''
    extensions = ['.py']
    outputfilename = ''
    percentsimilar = 95
    # 85 seemed to turn up the most likely candidates for copying solutions.
    # 95 seemed to work well for finding students copying each other.

    studentfilenamedata = splitfilenames(path, extensions)
    write2excel(path, studentfilenamedata, outputfilename)

    # only really useful when the submissions are code or text files
    # copiesfound = scanforcopying(path, extensions, percentsimilar)
    # for i in copiesfound:
    #     print(i)
    # solutionsfound = scanforsoltuions(path, extensions, percentsimilar)
    # for i in solutionsfound:
    #     print(i)

    # DO THIS LAST (For now at least. I'll fix it later.)
    removenumbers(path, extensions)


# TODO: Objectify the whole thing
if __name__ == '__main__':
    __example__()
