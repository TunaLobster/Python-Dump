import subprocess as sp

foils = ['0009', '0012', '0015', '2415', '4412', '4415', '23012']

ps = sp.Popen([r'C:\Users\charl\Desktop\XFOIL6.99\xfoil.exe'], stdin=sp.PIPE, stdout=None, stderr=None)


def issueCmd(cmd, echo=True):
    ps.stdin.write('{0}\n'.format(cmd).encode())  # Definitely better ways to encode, but nah.
    if echo:
        print(cmd)


def quitxfoil():
    issueCmd('QUIT')
    print('exited XFoil')


def x1():
    for i in foils:
        issueCmd('NACA ' + i)  # select foil
        issueCmd('OPER')  # open oper menu
        issueCmd('ITER 1000')
        issueCmd('PACC')  # polar accumulation
        issueCmd(i + 'invisc.txt')  # output file
        issueCmd('')  # no dump file
        issueCmd('ASEQ')  # alfa sequence
        issueCmd('0')  # start alpha
        issueCmd('12')  # end alpha
        issueCmd('1')  # alpha step
        issueCmd('PACC')
        issueCmd('')  # xfoil menu
        issueCmd('')  # double check to main menu


def x2():
    pass
    issueCmd('')


x1()
x2()
