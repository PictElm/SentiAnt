import os
import sys

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

def start(registered, turnsLimit=10):
    for main in registered:
        s = world.settings['worldSize']
        x, y = access.RNG.randrange(s), access.RNG.randrange(s)
        world.addNest(Queen(x, y, main[0], main[1]).nest)

    finished = False
    counter = 0

    seq = access.seqstart("game")

    access.info("Starting GUI")
    graph.start()

    while not finished and counter < turnsLimit:
        subseq = access.seqstart("turn" + str(counter), under=seq)
        world.turn()
        graph.update()
        access.seqend(subseq)

        counter+= 1

    graph.end()
    access.seqend(seq)

    access.info("Simulation returned.")

if __name__ == '__main__':
    world = World()
    start(load(world.settings['playersDirectory']))
