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

from sentiant.core import access


class Nest:
    def __init__(self, queen, color):
        self.queen = queen
        self.ants = []
        self.color = color

        self.queen.nest = self



class Queen:
    def __init__(self, posLowerX, posLowerY, callback, color):
        self.x = posLowerX
        self.y = posLowerY
        self.run = callback
        self.nest = Nest(self, color)
        self.around = [(-1, +0), (-1, +1), (+0, -1), (+0, +2),
                       (+1, -1), (+1, +2), (+2, +0), (+2, +1) ]

    def createInput(self, world):
        """ Create list of ressources availables around the queen
        """
        rPheros = []

        # creating pheromones list
        for ph in world.pheros:
            if ph.isInRange(self.x+0, self.y+0) or \
               ph.isInRange(self.x+0, self.y+1) or \
               ph.isInRange(self.x+1, self.y+0) or \
               ph.isInRange(self.x+1, self.y+1):
                rPheros.append(access.APhero(ph, self))

        # creating list of available resources around
        rRes = [(x, y, world[world.resT, self.x+x, self.y+y] and not \
                world[world.antT, self.x+x, self.y+y]) for x,y in self.around]

        return rRes, rPheros



class Ant:
    def __init__(self, posX, posY, nest, callback):
        self.run = callback
        self.nest = nest
        self.x = posX
        self.y = posY
        self.isHurt = False
        self.wasHurt = False
        self.isCarrying = False
        self.age = 0

    def __bool__(self):
        return True

    def createInput(self, world):
        """ Crops map and selects pheromones to input
        """
        s = access.settings['viewDistance']
        hs = s // 2

        rMap = [[~access.UNKNOWN for k in range(s)] for k in range(s)]
        rPheros = []
        rOnPos = None

        # creating pheromones list
        for ph in world.pheros:
            if ph.isInRange(self.x, self.y):
                rPheros.append(access.APhero(ph, self))
                if self.x == ph.x and self.y == ph.y:
                    rOnPos = ph

        # creating view map
        for i in range(s):
            for j in range(s) if i in [0, s - 1] else [0, s - 1]:
                if (i, j) == (hs, hs):
                    r[i][j] = world[world.mapT, self.x, self.y]
                    continue
                
                l = abs(i - hs) + abs(j - hs)
                u, v = float(i - hs) / l, float(j - hs) / l
                
                bla = False
                for k in range(l + 1):
                    a, b = int(self.x + k*u), int(self.y + k*v)
                    tile = world[world.mapT, a, b]

                    if world[world.antT, a, b]:
                        tile|= access.ANT_ON_TILE

                    if world[world.resT, a, b]:
                        tile|= access.RES_ON_TILE

                    if rMap[int(hs + k*u)][int(hs + k*v)] == ~access.UNKNOWN:
                        rMap[int(hs + k*u)][int(hs + k*v)] = access.UNKNOWN \
                                                               if bla else tile
                    bla|= tile & access.WALL

        return rMap, rPheros, rOnPos



class Phero:
    def __init__(self, posX, posY, value):
        self.decay = 0
        self.x = posX
        self.y = posY
        self.value = value

    def isInRange(posX, posY):
        x, y = world.coords(posX - self.x, posY - self.y)
        return x + y < access.settings['pheroRange'] - self.decay
