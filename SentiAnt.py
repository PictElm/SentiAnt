import os
import sys

from sentiant.core import World, Nest, Queen, access


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
    world = World()

    for main in registered:
        s = world.settings['worldSize']
        x, y = s // 2, s // 2 #access.RNG.randrange(s), access.RNG.randrange(s)
        world.addNest(Queen(x, y, main[0], main[1]).nest)

    finished = False
    counter = 0

    seq = access.seqstart("game")

    while not finished and counter < turnsLimit:
        subseq = access.seqstart("turn" + str(counter), under=seq)
        world.turn()
        access.seqend(subseq)

        counter+= 1


if __name__ == '__main__':
    start(load(sys.argv[1] if 1 < len(sys.argv) \
          else os.curdir + "/sentiant/player/"))
    #start(load(os.curdir + "/sentiant/player/"))
