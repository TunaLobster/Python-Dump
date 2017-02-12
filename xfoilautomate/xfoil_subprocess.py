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
        issueCmd('naca' + i + 'invisc.txt')  # output file
        issueCmd('')  # no dump file
        issueCmd('ASEQ')  # alfa sequence
        issueCmd('0')  # start alpha
        issueCmd('12')  # end alpha
        issueCmd('.5')  # alpha step
        issueCmd('PACC')  # disable polar accumulation
        issueCmd('PPLO')  # plot polars, lift curve
        issueCmd('')  # xfoil menu
        issueCmd('')  # double check to main menu
    issueCmd('PLOP')  # enter plot options menu
    issueCmd('C, F')  # add color option to postscript file
    issueCmd('')  # xfoil menu
    issueCmd('OPER')  # open oper menu
    issueCmd('HARD')  # generate plot.ps file
    issueCmd('')  # xfoil menu
    issueCmd('')  # double check to main menu


def x2(re):  # re as string
    issueCmd('NACA 4512')  # dummy foil to turn on viscosit
    issueCmd('OPER')
    issueCmd('VISC')
    issueCmd(re)
    issueCmd('')
    for i in foils:
        issueCmd('NACA ' + i)  # select foil
        issueCmd('OPER')  # open oper menu
        # issueCmd('RE')  # set Reynolds Number, Re
        # issueCmd(re)
        issueCmd('ITER 1000')  # change iteration limit
        issueCmd('PACC')  # polar accumulation
        issueCmd('naca' + i + 'visc.txt')  # output file
        issueCmd('')  # no dump file
        issueCmd('ASEQ')  # alfa sequence
        issueCmd('0')  # start alpha
        issueCmd('12')  # end alpha
        issueCmd('.5')  # alpha step
        issueCmd('PACC')  # disable polar accumulation
        issueCmd('PPLO')  # plot polars, lift curve
        issueCmd('')  # xfoil menu
        issueCmd('')  # double check to main menu
    issueCmd('PLOP')  # enter plot options menu
    issueCmd('C, F')  # add color option to postscript file
    issueCmd('')  # xfoil menu
    issueCmd('OPER')  # open oper menu
    issueCmd('HARD')  # generate plot.ps file
    issueCmd('')  # xfoil menu
    issueCmd('')  # double check to main menu

# must be run separately or each will be appended to plot.ps for a very weird looking graph.
# need to make feature request to xfoil to name HARD command .ps output
# x1()
x2(500000)
