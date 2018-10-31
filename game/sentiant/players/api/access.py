"""
   Copyright 2018 Grenier Celestin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from random import Random
from time import time

# `RNG` is you random number generator: use this to implement randomness in
# your algorithms, this way any simulation can be reproduces as long as you
# have the seed (given at the end of simulation).
RNG = Random()


NOT_FOUND     = -1

# The following directions are to use in combination with:
# `ATTACK_ON`, `MOVE_TO` or `DIG_AT`
NORTH         = 1
SOUTH         = NORTH << 1
EAST          = SOUTH << 1
WEAST         = EAST << 1

# Those are the moves you may use for (return from) you ants' algorithms.
ATTACK_ON     = WEAST << 1
MOVE_TO       = ATTACK_ON << 1
TAKE_RES      = MOVE_TO << 1
DROP_RES      = TAKE_RES
DIG_AT        = DROP_RES << 1
WAIT          = DIG_AT << 1

# This may be the second value you returns to either preserve a pheromone on
# the same tile as your's or to ignore it.
REFRESH_PHERO = WAIT << 1
KEEP_PHERO    = REFRESH_PHERO << 1

# The following flags are the ones to test whene reading the `AView` object
# passed to your ant.
WALL          = KEEP_PHERO << 1
ROCK          = WALL << 1
UNKNOWN       = ROCK << 1
ANT_ON_TILE   = UNKNOWN << 1
RES_ON_TILE   = ANT_ON_TILE << 1

# Actually, I don't think this is ever used...
EMPTY         = 0


# You can find description of the settings in the `settings.config` file.
# As this is a dictionary, you may use the name of a setting as key to get its
# value.
settings = {}

def loadSettings(configFile="sentiant/settings.config"):
    """ Loads all the settings from the specified file. Only works once as
        you don't need it in your code! Also set the seed from settings
        (or from `time.time()` if none provided).
    """
    if settings:
        return

    for it in open(configFile).readlines():
        if it[0] not in (';', '#'):
            k, v = it.strip().replace(' ', '').split(':')
            settings.update({ k: int(v) if v.isnumeric() else v })

    if 'randomSeed' not in settings.keys:
        settings['randomSeed'] = time()
    RNG.seed(settings['randomSeed'])
    RNG.seed = lambda *x: warning("You's not supposed to do that!") # trying...


class AQueen:
    """ A structue that allows you to access your run function and your color.
    """
    def __init__(self, queen):
        self.run = queen.run
        self.color = queen.nest.color


class AAnt:
    """ A structure that allows you to access:
        + `x` and `y`: position in the `AView` object... you dont need it, it's
            always centered on you;
        + `run`: the same function you using;
        + `color`: you color... (althrough don't expect this to stick around in
            futues versions!);
        + `isHurt`: weather you've been hurt once and are about to die;
        + `isCarrying`: weather you's carrying -the game- a resource.
    """
    def __init__(self, ant):
        self.x = settings['viewDistance'] // 2
        self.y = settings['viewDistance'] // 2
        self.run = ant.run
        self.color = ant.nest.color
        self.isHurt = ant.isHurt
        self.isCarrying = ant.isCarrying


class APhero:
    """ A structure that holds:
        + `x` and `y`: the position of the pheromone on the `AView`, relative
            to you;
        + `value`: its ID, from 0 to 15 included;
        + `decay`: its decaying progress form 0 to `settings: pheroRange`.
    """
    def __init__(self, phero, relateAnt):
        self.x = phero.x - relateAnt.x + settings['viewDistance'] // 2
        self.y = phero.y - relateAnt.x + settings['viewDistance'] // 2
        self.value = phero.value
        self.decay = phero.decay


class AView:
    """ A structure to access a tile's properties up to
        `settings: viewDistance` (=`size`) from you.
        To access any tile relative to you, you should access `(x, y)` like so:
            ``` view[x, y] ```
        .. so that you're, in fact, in the center of the view.
    """
    def __init__(self, view):
        self.view = view
        self.size = len(view)

    def __getitem__(self, xy):
        x, y = xy
        return self.view[self.size // 2 + x][self.size // 2 + y]


seqname = {}
seqlast = []

def stdout(s, end="\n", start="", seq=False):
    """ Standard output, you don't need to use it directly.

        This will (one day), with `settings: logsDirectory` allow the logs to
        be available in:
        + `stdout.log` file with anything that was logged;
        + `[teamname].log` file for what relates to a team.
        (+ `stderr.log`, `[mainseq]/[subseq]/[lastseq].log`, `turn[N].log`, ..)
    """
    print(start, end=" ")

    if seq and seqlast:
        seq = seqname[seq if seq in seqname.keys() else seqlast[-1]]
        print("<" + seq + "> ", end="")

    print(s, end=end)

def info(s, seq=True):
    """ Use that to ouput an information. """
    stdout(s, start="[Info]", seq=seq)

def warning(s, seq=True):
    """ Use that to ouput a warning. """
    stdout(s, start="[Warn]", seq=seq)

def error(s, seq=True):
    """ Use that to ouput an error. """
    stdout(s, start="[Rror]", seq=seq)

def debug(s, seq=True):
    """ Use that to ouput a debug message. """
    stdout(s, start="[Dbug]", seq=seq)

def newline():
    """ Use that to jump a new (empty) line. """
    stdout("")

def seqstart(name, under=''):
    """ Sequences allows you to organise your logs.

        To start a new sequence, use this function. You may save its ouputs
        (ID) in a local variable to use with `seqend`.

        When a sequence was started any new messages will, by default, be
        associated with this running sequence. To temporarily prevent this
        behaviour, you can specify the keyword argument `seq=False` in any
        messaging function.
    """
    if under != '':
        if under in seqname.keys():
            under = seqname[under]
        under+= '.'

    seqlast.append(1 if len(seqlast) < 1 else seqlast[-1] + 1)
    seqname.update({ seqlast[-1]: under + name })

    newline()
    info("started;", seq=seqlast[-1])

    return seqlast[-1]

def seqend(seq=-1):
    """ Sequences allows you to organise your logs.

        To end a (started) sequence, use this function. You sould specify
        which sequence you want to end by giving the ID you stored from calling
        `seqstart`. If you don't specify any ID, the latest sequence started
        will be ended. (Yes, you can lose the master sequence call `game` or
        the sub-sequence `turn[N]`, but you would be ruinnig your own logs...)
    """
    seq = seq if seq in seqname.keys() else seqlast[-1]

    info("ended.", seq=seq)
    newline()

    seqlast.remove(seq)
    name = seqname.pop(seq)

    return seqname
