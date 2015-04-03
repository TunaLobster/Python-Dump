#!C:\Python27

#For 500,000 mutables, this takes WAY to long. Look for better options
import sys

orgFile = open('InputList.txt','r')
newFile = open('SortedList.txt','w')

unsortedList = [line.strip() for line in orgFile]

def bubble_sort(list):
    for i in reversed(range(len(list))):
        finished = True
        for j in range(i):
            if list[j] > list[j + 1]:
                list[j], list[j + 1] = list[j + 1], list[j]
                finished = False
        if finished:
            break
    return list

sortedList = bubble_sort(unsortedList)

for i in sortedList:
    newFile.write("%s\n" % i)

orgFile.close()
newFile.clsoe()