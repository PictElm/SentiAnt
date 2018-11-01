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

import sentiant.players.api.access as access
import sentiant.graph as graph
from sentiant.parts import Ant, Phero


class World:
    def __init__(self):
        self.nests = []
        self.pheros = []

        s = access.settings['worldSize']
        self.antT = [[False for k in range(s)] for k in range(s)]
        self.resT = [[False for k in range(s)] for k in range(s)]
        self.mapT = [[access.WALL for k in range(s)] for k in range(s)]

    def generate(self):
        s = access.settings['worldSize']

        p = access.settings['rocksPercent']
        for k in range(int(s * s * p / 100.)):
            i, j = access.RNG.randrange(s), access.RNG.randrange(s)
            self[self.mapT, i, j]|= access.ROCK

        a = access.settings['resAmount']
        for k in range(a):
            i, j = access.RNG.randrange(s), access.RNG.randrange(s)
            while self[self.resT, i, j]:
                i, j = access.RNG.randrange(s), access.RNG.randrange(s)
            self[self.resT, i, j] = True
            self[self.mapT, i, j]^= access.ROCK

        return self

    def addNest(self, nest):
        for i in range(-3, 5):
            for j in range(-3, 5):
                if abs(i-.5) + abs(j-.5) < 5:
                    self[self.mapT, nest.queen.x + i, nest.queen.y + j] = \
                                                                   access.EMPTY

        for i, j in nest.queen.around:
            self[self.resT, nest.queen.x + i, nest.queen.y + j] = True

        for i in range(2):
            for j in range(2):
                self[self.mapT, nest.queen.x+i, nest.queen.y+j]|= access.ROCK
                self[self.antT, nest.queen.x+i, nest.queen.y+j] = True

        graph.drawQueen(nest.queen.x, nest.queen.y)

        self.nests.append(nest)

    def getAntByPos(self, x, y):
        return self[self.antT, x, y]

    def coords(self, x, y):
        s = access.settings['worldSize']
        if not x in range(s) or not y in range(s):
            return x % s, y % s
        return x, y

    def __setitem__(self, Txy, v):
        T, x, y = Txy
        x, y = self.coords(x, y)
        T[x][y] = v

        flags = graph.EMPTY

        if self.antT[x][y]:
            flags|= graph.ANT

        if self.resT[x][y]:
            flags|= graph.RES

        if self.mapT[x][y] & access.WALL:
            flags|= graph.WALL

        if self.mapT[x][y] & access.ROCK and not self.antT[x][y]:
            flags|= graph.ROCK

        graph.updateTile(x, y, flags)

    def __getitem__(self, Txy):
        T, x, y = Txy
        x, y = self.coords(x, y)
        return T[x][y]

    def isFinished(self):
        return False

    def turn(self):
        for nest in self.nests:
            queen = nest.queen
            resPos, pheros = queen.createInput(self)
            action = queen.run(access.AQueen(queen), resPos, pheros)

            if action != access.WAIT and isinstance(action, tuple) \
                                         or isinstance(action, list):
                posX, posY, cb = action
                posX+= queen.x
                posY+= queen.y

                if self[self.resT, posX, posY] == True:
                    nest.ants.append(Ant(posX, posY, nest, cb))

                    self[self.resT, posX, posY] = False
                    self[self.antT, posX, posY] = True

                    s = access.settings['worldSize']
                    i, j = access.RNG.randrange(s), access.RNG.randrange(s)
                    while self[self.resT, i, j]:
                        i, j = access.RNG.randrange(s), access.RNG.randrange(s)
                    self[self.resT, i, j] = True

        beeings = sum([n.ants for n in self.nests], [])
        access.RNG.shuffle(beeings)

        toMove = []
        toHurt = []

        for ant in beeings:
            ant.x, ant.y = self.coords(ant.x, ant.y)
            ant.wasHurt = ant.isHurt
            ant.age+= 1

            map, phL, onPos = ant.createInput(self)
            action, value = ant.run(access.AAnt(ant), access.AView(map), phL)

            # pheromone processing
            if isinstance(onPos, Phero):
                onPos.decay-= 1
                if value == access.REFRESH_PHERO:
                    onPos.decay = 0
            elif value != access.KEEP_PHERO and value in range(16):
                self.pheros.append(Phero(ant.x, ant.y, value))

            # action processing
            if action & access.ATTACK_ON:
                target = None
                
                if action & access.NORTH:
                    target = self.getAntByPos(ant.x, ant.y + 1)
                elif action & access.SOUTH:
                    target = self.getAntByPos(ant.x, ant.y - 1)
                elif action & access.EAST:
                    target = self.getAntByPos(ant.x + 1, ant.y)
                elif action & access.WEAST:
                    target = self.getAntByPos(ant.x - 1, ant.y)
                    
                if target and target != access.NOT_FOUND:
                    toHurt.append(target)
                    
            elif action & access.MOVE_TO:
                dest = None
                
                if action & access.NORTH:
                    dest = (ant.x, ant.y + 1)
                elif action & access.SOUTH:
                    dest = (ant.x, ant.y - 1)
                elif action & access.EAST:
                    dest = (ant.x + 1, ant.y)
                elif action & access.WEAST:
                    dest = (ant.x - 1, ant.y)
                    
                if dest and not self[self.antT, dest[0], dest[1]] \
                   and not self[self.mapT, dest[0], dest[1]] & access.WALL:
                    toMove.append((ant, dest[0], dest[1]))
                    self[self.antT, dest[0], dest[1]] = ant

            elif action & access.TAKE_RES and not ant.isCarrying \
                 and self[self.resT, ant.x, ant.y]:
                self[self.resT, ant.x, ant.y] = False
                ant.isCarrying = True

            elif action & access.DROP_RES and ant.isCarrying \
                 and not self[self.resT, ant.x, ant.y]:
                self[self.resT, ant.x, ant.y] = True
                ant.isCarrying = False

            elif action & access.DIG_AT:
                dest = None
                
                if action & access.NORTH:
                    dest = (ant.x, ant.y + 1)
                elif action & access.SOUTH:
                    dest = (ant.x, ant.y - 1)
                elif action & access.EAST:
                    dest = (ant.x + 1, ant.y)
                elif action & access.WEAST:
                    dest = (ant.x - 1, ant.y)

                if dest and not self[self.mapT,dest[0],dest[1]] & access.ROCK \
                   and self[self.mapT, dest[0], dest[1]] & access.WALL:
                    self[self.mapT, dest[0], dest[1]]^= access.WALL

        for ant in toHurt:
            if ant.isHurt:
                self[self.resT, ant.x, ant.y] = ant.isCarrying
                self[self.antT, ant.x, ant.y] = False
                ant.nest.remove(ant)
            else:
                ant.isHurt = True

        for ant, toX, toY in toMove:
            self[self.antT, ant.x, ant.y] = False
            ant.x, ant.y = toX, toY
