import re

def sanitize(s: str) -> str:
    ## The regular expression below matches < > : " / \ | ? * and ASCII control characters (0-31)
    ## to exclude them as they are disallowd in file names
    res = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', s.strip())
    return ' '.join(res.split())
