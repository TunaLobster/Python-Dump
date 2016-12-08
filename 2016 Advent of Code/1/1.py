#!C:\Program Files\Python35

route = 'R4, R4, L1, R3, L5, R2, R5, R1, L4, R3, L5, R2, L3, L4, L3, R1, R5, R1, L3, L1, R3, L1, R2, R2, L2, R5, L3,' \
        ' L4, R4, R4, R2, L4, L1, R5, L1, L4, R4, L1, R1, L2, R5, L2, L3, R2, R1, L194, R2, L4, R49, R1, R3, L5, L4, ' \
        'L1, R4, R2, R1, L5, R3, L5, L4, R4, R4, L2, L3, R78, L5, R4, R191, R4, R3, R1, L2, R1, R3, L1, R3, R4, R2, L2,' \
        ' R1, R4, L5, R2, L2, L4, L2, R1, R2, L3, R5, R2, L3, L3, R3, L1, L1, R5, L4, L4, L2, R5, R1, R4, L3, L5, L4,' \
        ' R5, L4, R5, R4, L3, L2, L5, R4, R3, L3, R1, L5, R5, R1, L3, R2, L5, R5, L3, R1, R4, L5, R4, R2, R3, L4,' \
        ' L5, R3, R4, L5, L5, R4, L4, L4, R1, R5, R3, L1, L4, L3, L4, R1, L5, L1, R2, R2, R4, R4, L5, R4, R1, L1, L1,' \
        ' L3, L5, L2, R4, L3, L5, L4, L1, R3'
# route = 'R5, L5, R5, R3'

turns = route.split(', ')
angle = 0 # East is 0
cardinals = [0, 0, 0, 0]  # N,S,E,W

for s in turns:
    if s[0] == 'R':
        angle = (angle - 90)%360
    elif s[0] == 'L':
        angle = (angle + 90)%360
    else:
        raise Exception('Character not "R" or "L"')

    blocks = int(s[1])
    if angle == 0:
        cardinals[2] += blocks  # East
    elif angle == 90:
        cardinals[0] += blocks  # North
    elif angle == 180:
        cardinals[3] += blocks  # West
    elif angle == 270:
        cardinals[1] += blocks  # South
    else:
        raise Exception('Not cardinal direction')

print(cardinals)

distance = abs(cardinals[1]-cardinals[0]) + abs(cardinals[3]-cardinals[2])
print(distance)
