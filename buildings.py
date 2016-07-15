import shutil


def chinese(height, width, floors):
    layout = {'topper': {'left': '\\', 'right': '/', 'span': '_'}, 'walls': '||'}
    _construct_building(layout, height, width, floors)


def roman(height, width, floors):
    layout = {'topper': {'left': '|', 'right': '|', 'span': '='}, 'walls': '‖‖'}
    _construct_building(layout, height, width, floors)


def _construct_building(layout, height, width, floors=1):
    size = shutil.get_terminal_size((80, 20))
    console_width = size.columns
    # console_height = size.lines
    for j in range(1, floors + 1):
        floor_width = int(width / floors) * j
        print((layout['topper']['left'] + layout['topper']['span'] * (floor_width - 2) + layout['topper'][
            'right']).center(console_width))
        for i in range(0, height):
            print((layout['walls'] + ' ' * (floor_width - 6) + layout['walls']).center(console_width))
