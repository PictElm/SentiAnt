import os
import sys
import time

from sentiant.core import World, access, graph
from sentiant.parts import Queen


def load(dirname):
    r = []
    prev = os.getcwd()
    os.chdir(dirname)

    seq = access.seqstart("loading")

    for filename in os.listdir():
        if ".py" in filename:
            name = filename[:-3]
            subseq = access.seqstart(name, under=seq)

            access.info("Importing main function from " + name +  "... ")
            try:
                r.append((__import__(name, fromlist=["main"]).main, name))
            except AttributeError as e:
                access.error("\tcould'n find `main` function, abort loading.")
            else:
                access.info("\tdone.")

            access.seqend(subseq)
    access.seqend(seq)

    os.chdir(prev)
    return r

def start(registered):
    for main in registered:
        s = access.settings['worldSize']
        x, y = access.RNG.randrange(s), access.RNG.randrange(s)
        world.addNest(Queen(x, y, main[0], main[1]).nest)

    loop.mainseq = access.seqstart("game")
    loop.counter = 0

    access.info("Starting GUI.")
    graph.start(loop)

def loop():
    subseq = access.seqstart("turn" + str(loop.counter), under=loop.mainseq)

    world.turn()
    graph.update(end if test(world.isFinished()) else loop)

    access.seqend(subseq)

def test(finished):
    loop.counter+= 1
    return finished or access.settings['turnsLimit'] < loop.counter + 1

def end():
    graph.end()
    access.seqend(loop.mainseq)

    access.info("Simulation returns.")

if __name__ == '__main__':
    access.loadSettings()
    graph.load()

    world = World().generate()

    start(load(access.settings['playersDirectory']))
