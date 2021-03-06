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

from sentiant.core import World, api, graph
from sentiant.parts import Queen

import os


def load(dirname):
    """ Load players algorithms.

        Try to loads a `main` function form every `.py` or `.pyc` (or even
        `.pyw`, by why would you?) files. If a file lack a `main` function,
        it is ignored.

        Return a list of `(main, name)` where `name` is the file associated
        (without its file extension).
    """
    loop.world = World()

    api.info("Loading GUI..")
    graph.load(loop.world)
    api.info("    ..done.")

    api.info("Generating world..")
    loop.world.generate()
    api.info("    ..done.")

    r = []
    prev = os.getcwd()
    os.chdir(dirname)

    pkgname = dirname.strip('./').replace('/', '.') + '.'

    seq = api.seqstart("loading")
    for filename in os.listdir():
        if filename[-3:] == '.py' or filename[-4:] in ('.pyc', '.pyw'):
            name = filename[:-3]
            subseq = api.seqstart(name)

            api.info("Importing main function from '" + name +  "'..")
            try:
                r.append((__import__(pkgname + name, fromlist=["main"]).main, \
                          name))
            except AttributeError as e:
                api.error( \
                    "    ..could'n find `main` function, abort loading. (" \
                        + str(e) + ")")
            else:
                api.info("    ..done.")

            api.seqend(subseq)
    api.seqend(seq)

    os.chdir(prev)
    return r

def start(registered):
    """ Start the simulation.

        + Spawn a queen (and its nest) for each contestant registered
            (returned from `load`).
        + Starts the main sequence.
        + Enter the main loop.
    """
    api.newline()
    api.info("Seed: " + str(api.settings('randomSeed')))
    api.info("(you will need this seed to replay the exact same game.)")
    api.newline()

    graph.makeColorMap([main[1] for main in registered])

    for main in registered:
        w, h = api.settings('worldSize')
        x, y = api.RNG.randrange(w), api.RNG.randrange(h)
        #x, y = world.generate.nextSpanwPosition()
        loop.world.addNest(Queen(x, y, main[0], main[1]).nest)

    loop.counter = 0

    loop.mainseq = api.seqstart("game")
    api.info("------------------- Start of simulation -------------------")

    graph.start(loop)

def loop():
    """ Make the `world.turn` then calls `graph.update` with either
        `end` or`loop` depending on `test`.
    """
    subseq = api.seqstart("turn:" + str(loop.counter), above=loop.mainseq)

    loop.world.turn()
    graph.update(end if test() else loop)

    api.seqend(subseq)

def test():
    """ Returns `True` if the simulation should be ended.

        Used in `loop` to check if the simulation is finished or should be
        stopped. In fact, the simulation is killed after
        `settings: turnsLimit`. Set this setting to a negative value to prevent
        this behavior.
    """
    loop.counter+= 1
    l = api.settings('turnsLimit')
    return loop.world.isFinished() or l < loop.counter + 1 and 0 < l

def end():
    """ End simulation. Also output the seed through `api.info`.
    """
    graph.end()

    api.info("------------------- End of simulation   -------------------")
    api.seqend(loop.mainseq)

    api.newline()
    api.info("Seed: " + str(api.settings('randomSeed')))
    api.info("(you will need this seed to replay the exact same game.)")


if __name__ == '__main__':
    if os.path.isdir('./game/'):
        os.chdir('./game/')

    api.loadSettings()
    start(load(api.settings('playersDirectory')))

    input("Press enter to continue. ")
