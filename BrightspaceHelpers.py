import os

import xlsxwriter
from fuzzywuzzy import fuzz

# external file with a list of solutions copied and pasted from the internet
import solutions


def filenameparser(filename):
    number, name, date, submission = filename.split(' - ', 3)
    lastname, firstname = name.split(' ', 1)
    return [number, lastname, firstname, date, submission]


def splitfilenames(path, ext):
    '''

    :param path: Directory sting where the submitted assignments were downloaded and extracted to
    :param ext: Tuple of stings of file extensions to scan for. Example: ('.py') or ('.sldprt','.sldasm')
    :return:
    '''
    allfiles = os.listdir(path)
    data = [['number', 'lastname', 'firstname', 'data', 'filename submitted']]
    for filename in allfiles:
        if not filename.lower().endswith(ext):
            continue
        # number, name, date, submission = filename.split(' - ', 3)
        # lastname, firstname = name.split(' ', 1)
        # data.append([number, lastname, firstname, date, submission])
        data.append(filenameparser(filename))
    return data


def removenumbers(path, ext):
    allfiles = os.listdir(path)
    for filename in allfiles:
        if not filename.lower().endswith(ext):
            continue
        os.rename(os.path.join(path, filename), os.path.join(path, filename[filename.find(' - ') + 3:]))


def write2excel(path, data, outputname):
    # note that xlsxwriter cannot overwrite existing files
    workbook = xlsxwriter.Workbook(os.path.join(path, outputname))
    worksheet = workbook.add_worksheet()
    for row in range(len(data)):
        for col in range(len(data[row])):
            worksheet.write(row, col, data[row][col])
    workbook.close()


def scanforsoltuions(path, ext, solutionslist, percent):
    allfiles = os.listdir(path)
    for filename in allfiles:
        if not filename.lower().endswith(ext):
            continue
        with open(os.path.join(path, filename), 'r') as studentfile:
            studentcode = studentfile.read()
        for soltuion in solutionslist:
            # token set ratio had best results
            score = fuzz.token_set_ratio(soltuion, studentcode)
            if score > percent:
                yield filenameparser(filename)[1:3], filenameparser(filename)[-1], score


def __example__():
    path = r'C:\Users\Charlie\Dropbox\Graduate\GTA\3403F18\Homework 4 - Upload Download Oct 2, 2018 402 PM'
    extension = '.py'
    outputfilename = '3403F18'
    solutionslist = solutions.solutionlist
    percentsimilar = 85  # 85 seemed to turn up the most likely candidates. It's not perfect though
    studentfilenamedata = splitfilenames(path, extension)
    write2excel(path, studentfilenamedata, outputfilename)
    solutionsfound = scanforsoltuions(path, extension, solutionslist, percentsimilar)
    for i in solutionsfound:
        print(i)
    # for i in filenamedata:
    #     print(i)

    # DO THIS LAST (For now at least. I'll fix it later.)
    removenumbers(path, extension)


if __name__ == '__main__':
    __example__()
