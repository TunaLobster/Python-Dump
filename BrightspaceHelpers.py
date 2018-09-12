import os


# Inital way of doing it. Better way would be to split on ' - ' and go from there.
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


# Here's a better way!
def splitfilenames(pwd, ext):
    allfiles = os.listdir(pwd)
    data = []
    for filename in allfiles:
        if not filename.endswith(ext):
            continue
        number, name, date, submission = filename.split(b' - ', 3)
        data.append([number, tuple(name.split(b' ')), date, submission])
    return data


def __main__():
    data = splitfilenames(b'C:\Users\Charlie\Downloads\Homework 2 - Upload Download Sep 11, 2018 749 PM', (b'.py'))
    for i in data:
        print(i)


if __name__ == '__main__':
    __main__()
