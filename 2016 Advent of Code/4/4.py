import re, collections, string


def caesar_cipher(n):
    az = string.ascii_lowercase
    x = n % len(az)
    return str.maketrans(az, az[x:] + az[:x])

ans1 = 0
regex = r'([a-z-]+)(\d+)\[(\w+)\]'
with open('input.txt') as fp:
    for code, sid, checksum in re.findall(regex, fp.read()):
        sid = int(sid)
        letters = ''.join(c for c in code if c in string.ascii_lowercase)
        tops = [(-n,c) for c,n in collections.Counter(letters).most_common()]
        ranked = ''.join(c for n,c in sorted(tops))
        if ranked.startswith(checksum):
            ans1 += sid
            decoded = code.translate(caesar_cipher(sid))
            if 'north' in decoded:
                print(decoded, sid)

print(ans1)
