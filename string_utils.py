import re

def sanitize(s: str):
    res = re.sub(r'[^\u0370-\u03ff\u1f00-\u1fffa-zA-Z0-9 ]', '', s.strip())
    ## the regular expression above matches all greek and latin characters, the digits and the space
    return ' '.join(res.split())
