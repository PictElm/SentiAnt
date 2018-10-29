from tkinter import Tk, Button, PhotoImage
import time

from sentiant.core import access


EMPTY = 0
ANT = 1
RES = 2
WALL = 1
ROCK = 2


root = Tk()

ant     = None
ant_res = None
res     = None
rock    = None
empty   = None

wallColor = "snow"
emptyColor = "snow"

grid = []
started = False

def updateTile(x, y, f):
    if not started:
        return

    img = empty

    if f & ANT:
        img = ant_res if f & RES else ant
    elif f & RES:
        img = res
    elif f & WALL:
        img = rock if f & ROCK else empty

    grid[x][y].update(image=img, bg=wallColor if f & WALL else emptyColor)

def update():
    root.update_idletasks()
    root.update()
    time.sleep(1 / access.settings['tickSpeed'])

def start():
    global grid, ant, ant_res, res, rock, empty, wallColor, emptyColor, started

    started = True

    ratio = int(250 / (access.settings['windowSize']\
                       /access.settings['worldSize']))
    dir = access.settings['texturesDirectory']

    ant     = PhotoImage(file=dir + "ant.png").subsample(ratio)
    ant_res = PhotoImage(file=dir + "ant_res.png").subsample(ratio)
    res     = PhotoImage(file=dir + "res.png").subsample(ratio)
    rock    = PhotoImage(file=dir + "rock.png").subsample(ratio)
    empty   = PhotoImage(file=dir + "empty.png").subsample(ratio)

    wallColor = "NavajoWhite4"
    emptyColor = "snow"

    s = access.settings['worldSize']
    for i in range(s):
        grid.append([])
        for j in range(s):
            b = Button(root, bg=wallColor, borderwidth=1, image=empty, \
                       command=lambda x=i, y=j: handlePress(x, y))
            b.grid(row=i, column=j)
            grid[-1].append(b)

    update()

def end():
    root.destroy()

def handlePress(x, y):
    access.info("Pressed: {}, {}".format(x, y))
