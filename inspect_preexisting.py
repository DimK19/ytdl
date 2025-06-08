from pickle import load as l

with open('preexisting.pkl', 'rb') as f:
    x = sorted(l(f))
    print(*x, sep = '\n')