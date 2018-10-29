from random import Random

seed = 9876543210
RNG = Random(seed)


NOT_FOUND     = -1 ^ 1

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
DIGGABLE      = WALL << 1
UNKNOWN       = DIGGABLE << 1

EMPTY         = ~WALL


settings = {}


class AQueen:
    def __init__(self, queen):
        self.run = queen.run
        self.color = queen.nest.color


class AAnt:
    def __init__(self, ant):
        self.x = world.settings['viewDistance'] // 2
        self.y = world.settings['viewDistance'] // 2
        self.run = ant.run
        self.color = ant.nest.color
        self.isHurt = ant.isHurt
        self.isCarrying = ant.isCarrying


class APhero:
    def __init__(self, phero, relateAnt):
        self.x = phero.x - relateAnt.x + world.settings['viewDistance'] // 2
        self.y = phero.y - relateAnt.x + world.settings['viewDistance'] // 2
        self.value = phero.value
        self.decay = phero.decay


seqT = {}
seqN = []

def stdout(s, end="\n", start="", seq=False):
    print(start, end=" ")
    if seq and seqN:
        seq = seqN[seq if seq in range(len(seqN)) else -1]
        print("<" + seq + "> ", end="")
        #(" <" + seq + ">" + "\t" * seqT[seq], end="")
    print(s, end=end)

def info(s, seq=True):
    stdout(s, end="\n", start="[info]", seq=seq)

def warning(s, seq=True):
    stdout(s, end="\n", start="[warn]", seq=seq)

def error(s, seq=True):
    stdout(s, end="\n", start="[err!]", seq=seq)

def debug(s, seq=True):
    stdout(s, end="\n", start="[heya]", seq=seq)

def newline():
    stdout("")

def seqstart(name, under=""):
    t = 1
    if under != "":
        if type(under) == int and under in range(len(seqN)):
            under = seqN[under]
        t+= seqT[under] if under in seqT.keys() else under.count('.')
        under+= "."

    seqN.append(under + name)
    seqT.update({ seqN[-1]: t })

    newline()
    info("started;", seq=seqN[-1])

    return len(seqN) - 1

def seqend(seq=-1):
    info("ended.\n", seq=seqN[seq])

    name = seqN.pop(seq)
    seqT.pop(name)

    return name
