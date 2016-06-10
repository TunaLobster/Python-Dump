import shutil


class _Main:
    _size = shutil.get_terminal_size((80, 20))
    _consoleWidth = _size.columns
    _consoleHeight = _size.lines

    def __init__(self):
        # self.size = shutil.get_terminal_size((80, 20))
        # consoleWidth = self.size.columns
        # consoleHeight = self.size.lines
        pass

    @staticmethod
    def constuctbuilding(layout, height=_consoleHeight, width=_consoleWidth):
        print((layout['topper']['left'] + layout['topper']['span'] * (width - 2) + layout['topper']['right']).center(_Main._consoleWidth))
        for i in range(0, height):
            print((layout['walls'] + ' ' * (width - 6) + layout['walls']).center(_Main._consoleWidth))


def chinese(height, width, floors):
    layout = {'topper': {'left': '\\', 'right': '/', 'span': '_'}, 'walls': '||'}
    _floorWidth = int(width / floors)
    for j in range(1, floors + 1):
        _Main.constuctbuilding(layout, height, _floorWidth * j)


def roman(height, width):
    layout = {'topper': {'left': '|', 'right': '|', 'span': '='}, 'walls': '#'}  # TODO Figure out a decent wall
    _Main.constuctbuilding(layout, height, width)
