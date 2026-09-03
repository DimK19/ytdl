from pickle import load as l

with open('preexisting.pkl', 'rb') as f:
    x = sorted([f"{t} [{v}]" for v, t in l(f).items()])
    print(*x, sep='\n')
    