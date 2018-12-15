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

from sentiant.core import api

import tkinter as tk


EMPTY = 0
WALL = 1
ANT = 2
RES = 4
ROCK = 8


root = tk.Tk()

ant     = None
ant_res = None
res     = None
rock    = None
empty   = None

queen   = [[None, None], [None, None]]

wallColor = "snow"
emptyColor = "snow"

grid = []

tileSize = 100

def load():
    global ant, ant_res, res, rock, empty, wallColor, emptyColor

    #ratio = int(250 / (api.settings('windowSize')\
    #                   /api.settings('worldSize')))
    global tileSize
    tileSize = api.settings('tileSize')
    ratio = 250 // tileSize
    dir = api.settings('texturesDirectory')

    ant     = tk.PhotoImage(file=dir + "ant.png").subsample(ratio)
    ant_res = tk.PhotoImage(file=dir + "ant_res.png").subsample(ratio)
    res     = tk.PhotoImage(file=dir + "res.png").subsample(ratio)
    rock    = tk.PhotoImage(file=dir + "rock.png").subsample(ratio)
    empty   = tk.PhotoImage(file=dir + "empty.png").subsample(ratio)

    for i in range(2):
        for j in range(2):
            filename = dir + "queen{}{}.png".format(1-j, i)
            queen[i][j] = tk.PhotoImage(file=filename).subsample(ratio)

    wallColor = api.settings('wallColor')
    emptyColor = api.settings('emptyColor')

    # configure window
    vsb = tk.Scrollbar(root, orient=tk.VERTICAL)
    vsb.grid(row=0, column=1, sticky=tk.N + tk.S)

    hsb = tk.Scrollbar(root, orient=tk.HORIZONTAL)
    hsb.grid(row=1, column=0, sticky=tk.E + tk.W)

    canvas = tk.Canvas(root, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    canvas.grid(row=0, column=0, sticky="news")

    vsb.config(command=canvas.yview)
    hsb.config(command=canvas.xview)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    frame = tk.Frame(canvas)

    s = api.settings('worldSize')
    for i in range(s):
        grid.append([])
        for j in range(s):
            b = tk.Label(frame, bg=wallColor, borderwidth=1, image=empty, \
                         text=" ", width=tileSize, height=tileSize, \
                         #command=lambda x=i, y=j: handlePress(x, y), \
                         fg=api.settings('textColor'), compound=tk.CENTER)
            b.grid(column=i, row=s-j+1)
            grid[-1].append(b)

    canvas.create_window(0, 0, window=frame)
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    root.bind_all("<MouseWheel>", lambda e: scroll(canvas, e))

def scroll(canvas, event):
    if event.state & 4:
        global tileSize
        tileSize+= event.delta // 120

        for row in grid:
            for it in row:
                it.configure(width=tileSize, height=tileSize)

        canvas.update_idletasks()
        root.update_idletasks()

    elif event.state & 1:
        canvas.xview_scroll(-event.delta // 120, "units")
    else:
        canvas.yview_scroll(-event.delta // 120, "units")

def start(mainloop):
    mainloop()
    root.mainloop()

def drawQueen(lowerX, lowerY):
    s = api.settings('worldSize')
    for i in range(2):
        for j in range(2):
            x, y = (lowerX + i) % s, (lowerY + j) % s
            grid[x][y].config(image=queen[i][j], bg=emptyColor)

def updateTile(x, y, f, ph):
    img = empty

    if f & ANT:
        img = ant_res if f & RES else ant
    elif f & RES:
        img = res
    elif f & ROCK:
        img = rock

    grid[x][y].config(bg=wallColor if f & WALL else emptyColor, \
                      image=img, text=ph)

def update(next):
    root.update_idletasks()
    root.update()
    root.after(int(1000 * 100. / api.settings('tickSpeed')), next)

def end():
    pass #root.destroy()

def handlePress(x, y):
    api.info("Pressed: {}, {}.".format(x, y))
