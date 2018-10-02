import os

import xlsxwriter


# Initial way of doing it. Better way would be to split on ' - ' and go from there.
def names(pwd):
    '''

    :param dir: A directory sting where the submitted assignments are held
    :return: A list of list names (last, first) from the files
    '''
    allfiles = os.listdir(pwd)
    names = []
    for filename in allfiles:
        name = filename[filename.find(b' - ') + 3:filename.find(b' - ', 17)]
        names.append(tuple(name.split(b' ')))
    return names


def turnindate(pwd):
    '''

    :param pwd: A directory sting where the submitted assignments are held
    :return: A list of dates when the files were submitted
    '''
    allfiles = os.listdir(pwd)
    dates = []
    for filename in allfiles:
        s = filename.find(b' - ', filename.find(b' - ') + 3) + 3
        date = filename[s:filename.find(b' - ', s)]
        dates.append(date)
    return dates


# Here is a better way!
def splitfilenames(pwd, ext):
    '''

    :param pwd: Directory sting where the submitted assignments were downloaded and extracted to
    :param ext: Tuple of stings of file extensions to scan for. Example: ('.py') or ('.sldprt','.sldasm')
    :return:
    '''
    allfiles = os.listdir(pwd)
    data = [['number', 'lastname', 'firstname', 'data', 'filename submitted']]
    for filename in allfiles:
        if not filename.lower().endswith(ext):
            continue
        number, name, date, submission = filename.decode('utf-8').split(' - ', 3)
        lastname, firstname = name.split(' ', 1)
        data.append([number, lastname, firstname, date, submission])
    return data


def removenumbers(pwd, ext):
    allfiles = os.listdir(pwd)
    for filename in allfiles:
        if not filename.lower().endswith(ext):
            continue
        os.rename(os.path.join(pwd, filename), os.path.join(pwd, filename[filename.find(b' - ') + 3:]))


def write2excel(path, data):
    # note that xlsxwriter cannot overwrite existing files
    workbook = xlsxwriter.Workbook(os.path.join(path, '1332F18 Lab2 grades.xlsx'))
    worksheet = workbook.add_worksheet()
    for row in range(len(data)):
        for col in range(len(data[row])):
            worksheet.write(row, col, data[row][col])
    workbook.close()


def __example__():
    path = b'C:\Users\Charlie\Dropbox\Graduate\GTA\3403F18\Homework 4 - Upload Download Oct 2, 2018 402 PM'
    extension = b'.py'
    filenamedata = splitfilenames(path, extension)
    write2excel(path, filenamedata)
    removenumbers(path, extension)


if __name__ == '__main__':
    __example__()
