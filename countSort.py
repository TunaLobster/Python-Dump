#!C:\Python27

# Open files
orgFile = open('InputList.txt', 'r')
newFile = open('SortedList.txt', 'w')

# Load the unsorted list from the unsorted file
unsortedList = [int(line.strip()) for line in orgFile]


# Define function to sort using count sorting alogorithm
def count_sort(list):
    # Find the maximum vale in list
    maxValue = 0
    for i in range(len(list)):
        if list[i] > maxValue:
            maxValue = list[i]

    # Make a new list of intergers that is the same length
    # as the maximum number of list
    countList = [0] * (maxValue + 1)

    # Count the occurance of each integer value in list and store
    # the count of the integer at the poistion of countList that
    # equals that integer value
    for i in list:
        countList[i] += 1

    # Make a new list that has the position the number of times
    # defined at the position
    j = 0
    for i in range(len(countList)):
        while 0 < countList[i]:
            list[j] = i
            j += 1
            countList[i] -= 1

    return list


# Sort the list of integers
sortedList = count_sort(unsortedList)

# Output sorted list to external txt file
for i in sortedList:
    newFile.write("%s\n" % i)

# Close the files
orgFile.close()
newFile.close()
