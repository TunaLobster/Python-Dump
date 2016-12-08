# import re
#
# f = open('input.txt').readlines()
# ip = [line.strip() for line in f]
# counter = 0
#
# for s in ip:
#     last_bracket = 0
#     while re.search(r'[a-z]+', s[last_bracket:]) is not None:
#         test = s[last_bracket:int(len(s[last_bracket:s.find('[', last_bracket)])/2 + 1)]
#         if test == test[::-1]:
#             counter += 1
#             print(s)
#         last_bracket = s.find(']', last_bracket)
#         print(last_bracket)
#
# print(counter)

import re


def abba(x):
    return any(a == d and b == c and a != b for a, b, c, d in zip(x, x[1:], x[2:], x[3:]))

lines = [re.split(r'\[([^\]]+)\]', line) for line in open('input.txt')]
parts = [(' '.join(p[::2]), ' '.join(p[1::2])) for p in lines]
print('Answer #1:', sum(abba(sn) and not(abba(hn)) for sn, hn in parts))
print('Answer #2:', sum(any(a == c and a != b and b+a+b in hn for a, b, c in zip(sn, sn[1:], sn[2:])) for sn, hn in parts))