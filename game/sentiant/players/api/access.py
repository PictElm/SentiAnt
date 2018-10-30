from random import Random
from time import time

seed = time()
RNG = Random(seed)


NOT_FOUND     = -1

NORTH         = 1
SOUTH         = NORTH << 1
EAST          = SOUTH << 1
WEAST         = EAST << 1

ATTACK_ON     = WEAST << 1
MOVE_TO       = ATTACK_ON << 1
TAKE_RES      = MOVE_TO << 1
DROP_RES      = TAKE_RES
DIG_AT        = DROP_RES << 1
SPAWN_FROM    = DIG_AT
WAIT          = SPAWN_FROM << 1

REFRESH_PHERO = WAIT << 1
KEEP_PHERO    = REFRESH_PHERO << 1

WALL          = KEEP_PHERO << 1
ROCK          = WALL << 1
UNKNOWN       = ROCK << 1

ANT_ON_TILE   = UNKNOWN << 1
RES_ON_TILE   = ANT_ON_TILE << 1

EMPTY         = 0


settings = {}

def loadSettings(configFile="sentiant/settings.config"):
    if settings:
        return

    for it in open(configFile).readlines():
        if ':' in it:
            k, v = it.strip().replace(' ', '').split(':')
            settings.update({ k: int(v) if v.isnumeric() else v })


class AQueen:
    def __init__(self, queen):
        self.run = queen.run
        self.color = queen.nest.color


class AAnt:
    def __init__(self, ant):
        self.x = settings['viewDistance'] // 2
        self.y = settings['viewDistance'] // 2
        self.run = ant.run
        self.color = ant.nest.color
        self.isHurt = ant.isHurt
        self.isCarrying = ant.isCarrying


class APhero:
    def __init__(self, phero, relateAnt):
        self.x = phero.x - relateAnt.x + settings['viewDistance'] // 2
        self.y = phero.y - relateAnt.x + settings['viewDistance'] // 2
        self.value = phero.value
        self.decay = phero.decay


class AView:
    def __init__(self, view):
        self.view = view
        self.size = len(view)

    def __getitem__(self, xy):
        x, y = xy
        return self.view[self.size // 2 + x][self.size // 2 + y]

seqname = {}
seqlast = []

def stdout(s, end="\n", start="", seq=False):
    print(start, end=" ")

    if seq and seqlast:
        seq = seqname[seq if seq in seqname.keys() else seqlast[-1]]
        print("<" + seq + "> ", end="")

    print(s, end=end)

def info(s, seq=True):
    stdout(s, start="[Info]", seq=seq)

def warning(s, seq=True):
    stdout(s, start="[Warn]", seq=seq)

def error(s, seq=True):
    stdout(s, start="[Rror]", seq=seq)

def debug(s, seq=True):
    stdout(s, start="[Dbug]", seq=seq)

def newline():
    stdout("")

def seqstart(name, under=''):
    if under != '':
        if under in seqname.keys():
            under = seqname[under]
        under+= '.'

    seqlast.append(1 if len(seqlast) < 1 else seqlast[-1] + 1)
    seqname.update({ seqlast[-1]: under + name })

    #newline()
    info("started;", seq=seqlast[-1])

    return seqlast[-1]

def seqend(seq=-1):
    seq = seq if seq in seqname.keys() else seqlast[-1]

    info("ended.", seq=seq)
    newline()

    seqlast.remove(seq)
    name = seqname.pop(seq)

    return seqname
