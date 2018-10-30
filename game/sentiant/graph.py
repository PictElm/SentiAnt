from tkinter import Tk, Button, PhotoImage

from sentiant.core import access


EMPTY = 0
WALL = 1
ANT = 2
RES = 4
ROCK = 8


root = Tk()

ant     = None
ant_res = None
res     = None
rock    = None
empty   = None

queen   = [[None, None], [None, None]]

wallColor = "snow"
emptyColor = "snow"

grid = []

def load():
    global ant, ant_res, res, rock, empty, wallColor, emptyColor

    ratio = int(250 / (access.settings['windowSize']\
                       /access.settings['worldSize']))
    dir = access.settings['texturesDirectory']

    ant     = PhotoImage(file=dir + "ant.png").subsample(ratio)
    ant_res = PhotoImage(file=dir + "ant_res.png").subsample(ratio)
    res     = PhotoImage(file=dir + "res.png").subsample(ratio)
    rock    = PhotoImage(file=dir + "rock.png").subsample(ratio)
    empty   = PhotoImage(file=dir + "empty.png").subsample(ratio)

    for i in range(2):
        for j in range(2):
            filename = dir + "queen{}{}.png".format(i, j)
            queen[i][j] = PhotoImage(file=filename).subsample(ratio)

    wallColor = access.settings['wallColor']
    emptyColor = access.settings['emptyColor']

    s = access.settings['worldSize']
    for i in range(s):
        grid.append([])
        for j in range(s):
            b = Button(root, bg=wallColor, borderwidth=1, image=empty, \
                       command=lambda x=i, y=j: handlePress(x, y))
            b.grid(row=i, column=j)
            grid[-1].append(b)

def start(mainloop):
    mainloop()
    root.mainloop()

def updateTile(x, y, f):
    img = empty

    if f & ANT:
        img = ant_res if f & RES else ant
    elif f & RES:
        img = res
    elif f & ROCK:
        img = rock

    grid[x][y].config(image=img, bg=wallColor if f & WALL else emptyColor)

def drawQueen(lowerX, lowerY):
    s = access.settings['worldSize']
    for i in range(2):
        for j in range(2):
            x, y = (lowerX + i) % s, (lowerY + j) % s
            grid[x][y].config(image=queen[i][j], bg=emptyColor)

def update(next):
    root.update_idletasks()
    root.update()
    root.after(int(1000 * 100. / access.settings['tickSpeed']), next)

def end():
    pass #root.destroy()

def handlePress(x, y):
    access.info("Pressed: {}, {}.".format(x, y))
