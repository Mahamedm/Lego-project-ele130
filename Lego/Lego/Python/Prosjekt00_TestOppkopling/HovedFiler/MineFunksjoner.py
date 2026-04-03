# Denne er å foretrekke siden kallet i Main.py gir mye informasjon
def UsingElements(Arg1, Arg2, para):
    return Arg1 + para*Arg2[-1] + para*Arg2[-2]


# Denne er ikke å foretrekke siden kallet i Main.py gir lite informasjon
def UsingLists(Arg1, Arg2, para):
    Arg1.append(Arg1[-1] + para*Arg2[-1] + para*Arg2[-2])

