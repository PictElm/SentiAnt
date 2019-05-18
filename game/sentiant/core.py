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

from sentiant import api
from sentiant import graph

from sentiant.parts import Queen, Ant, Phero


class World:
    def __init__(self):
        self.nests = []
        self.pheros = []

        w, h = api.settings('worldSize')
        self.antT = [[False for k in range(h)] for k in range(w)]
        self.mapT = [[api.WALL for k in range(h)] for k in range(w)]

    def generate(self):
        w, h = api.settings('worldSize')

        p = api.settings('rocksPercent')
        for k in range(int(w * h * p / 100.)):
            i, j = api.RNG.randrange(w), api.RNG.randrange(h)
            self[self.mapT, i, j]|= api.ROCK

        a = api.settings('resAmount')
        for k in range(a):
            i, j = api.RNG.randrange(w), api.RNG.randrange(h)
            while self[self.mapT, i, j] & api.RESOURCE:
                i, j = api.RNG.randrange(w), api.RNG.randrange(h)
            self[self.mapT, i, j]|= api.RESOURCE
            if self[self.mapT, i, j] & api.ROCK:
                self[self.mapT, i, j]^= api.ROCK

        return self

    def addNest(self, nest):
        for i in range(-3, 5):
            for j in range(-3, 5):
                if abs(i-.5) + abs(j-.5) < 5:
                    self[self.mapT, nest.queen.x + i, nest.queen.y + j] = \
                                                                   api.EMPTY

        for i, j in nest.queen.around:
            self[self.mapT, nest.queen.x +i, nest.queen.y +j]|= api.RESOURCE

        for i in range(2):
            for j in range(2):
                self[self.antT, nest.queen.x +i, nest.queen.y +j] = nest.queen

        graph.drawQueen(nest.queen.x, nest.queen.y, nest.color)

        self.nests.append(nest)

    def coords(self, x, y):
        w, h = api.settings('worldSize')
        if not x in range(w) or not y in range(h):
            return x % w, y % h
        return x, y

    def __setitem__(self, Txy, v):
        T, x, y = Txy
        x, y = self.coords(x, y)
        T[x][y] = v

        flags = graph.EMPTY
        name = ""

        if isinstance(self.antT[x][y], Ant):
            flags|= graph.ANT
            name = self.antT[x][y].nest.color

        if self.mapT[x][y] & api.RESOURCE:
            flags|= graph.RES

        if self.mapT[x][y] & api.WALL:
            flags|= graph.WALL

        if self.mapT[x][y] & api.ROCK:
            flags|= graph.ROCK

        ph, dk = -1, -1
        for phero in self.pheros:
            if phero.x == x and phero.y == y:
                ph, dk = phero.value, phero.decay

        graph.updateTile(x, y, flags, \
                         " " if ph + dk == -2 else str(ph) + ", " + str(dk), \
                         name)

    def __getitem__(self, Txy):
        T, x, y = Txy
        x, y = self.coords(x, y)
        return T[x][y]

    def isFinished(self):
        return False

    def turn(self):
        queensSeq = api.seqstart("queens")

        for nest in self.nests:
            queen = nest.queen

            resPos, pheros = queen.createInput(self)
            aqueen = api.AQueen(queen)

            queenSeq = api.seqstart(queen.nest.color)
            action = queen.run(aqueen, resPos, pheros)
            queen.memory.update(aqueen.memory)
            api.seqend(queenSeq)

            if action != api.WAIT and ( isinstance(action, tuple) \
                                        or isinstance(action, list) ):
                posX, posY, cb = action
                posX, posY = self.coords(posX + queen.x, posY + queen.y)

                if self[self.mapT, posX, posY] & api.RESOURCE:
                    newAnt = Ant(posX, posY, nest, cb)
                    nest.append(newAnt)

                    self[self.mapT, posX, posY]^= api.RESOURCE
                    self[self.antT, posX, posY] = newAnt

                    # send used resource back to the world
                    w, h = api.settings('worldSize')
                    i, j = api.RNG.randrange(w), api.RNG.randrange(h)
                    while self[self.mapT, i, j] & api.RESOURCE \
                            or self[self.mapT, i, j] & api.ROCK \
                            or isinstance(self[self.antT, i, j], Queen):
                        i, j = api.RNG.randrange(w), api.RNG.randrange(h)
                    self[self.mapT, i, j]|= api.RESOURCE

        api.seqend(queensSeq)

        antsSeq = api.seqstart("ants")

        beeings = sum([n.ants for n in self.nests], [])
        api.RNG.shuffle(beeings)

        toMove = []
        toHurt = []

        for ant in beeings:
            map, ants, phL, onPos = ant.createInput(self)
            aant, aview = api.AAnt(ant), api.AView(map, ants)

            antSeq = api.seqstart(ant.nest.color + ":" + str(id(ant))[-3:])
            action, value = ant.run(aant, aview, phL)
            ant.memory.update(aant.memory)
            api.seqend(antSeq)

            # pheromone processing
            if isinstance(onPos, Phero):
                onPos.decay+= 1

                if value == api.REFRESH_PHERO:
                    onPos.decay = 0
                elif value in range(16):
                    onPos.x, onPos.y = ant.x, ant.y
                    onPos.decay, onPos.value = 0, value

                if onPos.decay == api.settings('pheroRange'):
                    self.pheros.remove(onPos)
                    self[self.mapT, onPos.x, onPos.y]+= 0

            elif value in range(16):
                self.pheros.append(Phero(ant.x, ant.y, value))
                self[self.mapT, ant.x, ant.y]+= 0

            # grown-up stuff
            if 0 < ant.age or True:
                # action processing
                dx, dy = api.asPosition(action)
                X, Y = self.coords(ant.x + dx, ant.y + dy)

                if action & api.ATTACK_ON and not ant.isCarrying:
                    if isinstance(self[self.antT, X, Y], Ant):
                        toHurt.append(self[self.antT, X, Y])

                elif action & api.MOVE_TO:
                    if not self[self.antT, X, Y] \
                       and not self[self.mapT, X, Y] & api.WALL:
                        toMove.append((ant, X, Y))
                        self[self.antT, X, Y] = ant

                elif action & api.TAKE_RES and not ant.isCarrying \
                     and self[self.mapT, ant.x, ant.y] & api.RESOURCE:
                    self[self.mapT, ant.x, ant.y]^= api.RESOURCE
                    ant.isCarrying = True

                elif action & api.DROP_RES and ant.isCarrying \
                     and not self[self.mapT, ant.x, ant.y] & api.RESOURCE:
                    self[self.mapT, ant.x, ant.y]|= api.RESOURCE
                    ant.isCarrying = False

                elif action & api.DIG_AT and not ant.isCarrying:
                    if not self[self.mapT, X, Y] & api.ROCK \
                       and self[self.mapT, X, Y] & api.WALL:
                        self[self.mapT, X, Y]^= api.WALL

            # others
            ant.x, ant.y = self.coords(ant.x, ant.y)
            ant.wasHurt = ant.isHurt
            ant.age+= 1

        for ant in toHurt:
            if not ant.isDead:
                if ant.isHurt:
                    if ant.isCarrying:
                        i, j = ant.x, ant.y
                        while self[self.mapT, i, j] & api.RESOURCE:
                            i, j = api.RNG.randint(-4,4), api.RNG.randint(-4,4)
                        self[self.mapT, i, j]|= api.RESOURCE

                    self[self.antT, ant.x, ant.y] = False
                    ant.nest.remove(ant)
                    ant.isDead = True
                else:
                    ant.isHurt = True

        for ant, toX, toY in toMove:
            if not ant.isDead:
                self[self.antT, ant.x, ant.y] = False
                ant.x, ant.y = toX, toY
            else:
                self[self.antT, toX, toY] = False

        api.seqend(antsSeq)
