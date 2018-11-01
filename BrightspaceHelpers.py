import os

import xlsxwriter
from fuzzywuzzy import fuzz


# TODO: I should probably write a generator for files that have the correct extension
# TODO: Write this to handle filenames without numbers
def filenameparser(filename):
    number, name, date, submission = filename.split(' - ', 3)
    lastname, firstname = name.split(' ', 1)
    return [number, lastname, firstname, date, submission]


def splitfilenames(path, ext):
    """

    :param path: Directory sting where the submitted assignments were downloaded and extracted to
    :param ext: Tuple of stings of file extensions to scan for. Example: ('.py') or ('.sldprt','.sldasm')
    :return:
    """
    allfiles = os.listdir(path)
    data = [['number', 'lastname', 'firstname', 'data', 'filename submitted']]
    for filename in allfiles:
        if not filename.lower().endswith(ext.lower()):
            continue
        # number, name, date, submission = filename.split(' - ', 3)
        # lastname, firstname = name.split(' ', 1)
        # data.append([number, lastname, firstname, date, submission])
        data.append(filenameparser(filename))
    return data


# TODO: Handle case of numbers not at start of files
def removenumbers(path, ext):
    allfiles = os.listdir(path)
    for filename in allfiles:
        if not filename.lower().endswith(ext.lower()):
            continue
        os.rename(os.path.join(path, filename), os.path.join(path, filename[filename.find(' - ') + 3:]))


def write2excel(path, data, outputname):
    # note that xlsxwriter cannot overwrite existing files
    if not outputname.lower().endswith('.xlsx'):
        outputname = '.'.join([outputname, 'xlsx'])
    workbook = xlsxwriter.Workbook(os.path.join(path, outputname))
    worksheet = workbook.add_worksheet()
    for row in range(len(data)):
        for col in range(len(data[row])):
            worksheet.write(row, col, data[row][col])
    workbook.close()


def scanforsoltuions(path, ext, percent):
    # external file with a list of solutions copied and pasted from the internet in a python list.
    # Example "solutions.py" file contents:
    # solutionlist = ['''copied from google result''','''students shouldn't do this''','''so many ways to tell''']
    import solutions
    solutionslist = solutions.solutionlist
    allfiles = os.listdir(path)
    for filename in allfiles:
        if not filename.lower().endswith(ext.lower()):
            continue
        with open(os.path.join(path, filename), 'r') as studentfile:
            studentcode = studentfile.read()
        for soltuion in solutionslist:
            # token set ratio had best results
            score = fuzz.token_set_ratio(soltuion, studentcode)
            if score > percent:
                yield filenameparser(filename)[1:3], filenameparser(filename)[-1], score


# TODO: Add function to compare students. Should be bigO(1/n)?
def __example__():
    path = r'C:\Users\Charlie\Dropbox\Graduate\GTA\3403F18\Grading\Homework 6 - Problem1 - Upload Download Oct 22, 2018 948 AM'
    extension = '.py'
    outputfilename = '3403F18 HW6 part1 grades'
    percentsimilar = 85  # 85 seemed to turn up the most likely candidates. It's not perfect though

    studentfilenamedata = splitfilenames(path, extension)
    write2excel(path, studentfilenamedata, outputfilename)

    # only really useful when the submissions are code or text files
    # solutionsfound = scanforsoltuions(path, extension, percentsimilar)
    # for i in solutionsfound:
    #     print(i)

    # DO THIS LAST (For now at least. I'll fix it later.)
    removenumbers(path, extension)


# TODO: Objectify the whole thing
if __name__ == '__main__':
    __example__()
