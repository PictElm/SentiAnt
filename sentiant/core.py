import sentiant.player.api.access as access
import os

class World:
    def __init__(self, configFile="sentiant/settings.config"):
        self.settings = {}

        for it in open(configFile).readlines():
            k, v = it.split(':')
            self.settings.update([(k, int(v))])
        access.settings.update(self.settings)
        
        self.nests = []
        self.pheros = []
        
        s = self.settings['worldSize']
        self.isAnt = [[False for k in range(s)] for k in range(s)]
        self.isRes = [[False for k in range(s)] for k in range(s)]
        self.map = [[access.WALL for k in range(s)] for k in range(s)]

        r = self.settings['rocksPercent']
        for k in range(int(s * s * r / 100)):
            self.map[access.RNG.randrange(s)][access.RNG.randrange(s)]

        a = self.settings['resAmount']
        for k in range(a):
            i, j = access.RNG.randrange(s), access.RNG.randrange(s)
            while self.isRes[i][j]:
                i, j = access.RNG.randrange(s), access.RNG.randrange(s)
            self.isRes[i][j]

    def addNest(self, nest):
        for i in range(-3, 5):
            for j in range(-3, 5):
                if abs(i-1) + abs(j-1) < 5:
                    self.map[nest.queen.x + i][nest.queen.y + j] = access.EMPTY

        for i, j in nest.queen.around:
            self.isRes[nest.queen.x + i][nest.queen.y + j] = True

        self.nests.append(nest)

    def getAntByPos(self, x, y):
        return self.isAnt[x][y]

    def turn(self):
        for nest in self.nests:
            queen = nest.queen
            resPos, pheros = queen.createInput(self)
            action = queen.run(access.AQueen(queen), resPos, pheros)

            if action != access.WAIT:
                posX, posY, cb = action

                if self.isRes[posX][posY] == False:
                    nest.ants.append(Ant(posX, posY, nest, cb))
                    self.isRes[posX][posY] = False
                    self.isAnt[posX][posY] = True

        beeings = sum([n.ants for n in self.nests], [])
        access.RNG.shuffle(beeings)

        toMove = []
        toHurt = []

        for ant in beeings:
            map, pheros, onPos = ant.createInput(self)
            action, value = ant.run(access.AAnt(ant), map, pheros)

            # pheromone processing
            if value == access.REFRESH_PHERO and isinstance(onPos, Phero):
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
                    
                if dest and not self.isAnt[dest[0]][dest[1]] \
                   and not self.map[dest[0]][dest[1]] & WALL:
                    toMove.append((ant, dest[0], dest[1]))
                    self.isAnt[dest[0]][dest[1]] = ant

            elif action & access.TAKE_RES and not ant.isCarrying \
                 and self.isRes[ant.x][ant.y]:
                self.isRes[ant.x][ant.y] = False
                ant.isCarrying = True

            elif action & access.DROP_RES and ant.isCarrying \
                 and not self.isRes[ant.x][ant.y]:
                self.isRes[ant.x][ant.y] = True
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

                if dest and self.map[dest[0]][dest[1]] & access.DIGGABLE \
                   and self.map[dest[0]][dest[1]] & access.WALL:
                    self.map[dest[0]][dest[1]]^= access.WALL

        for ant in toHurt:
            if ant.isHurt:
                self.isRes[ant.x][ant.y] = ant.isCarrying
                self.isAnt[ant.x][ant.y] = False
                ant.nest.remove(ant)
            else:
                ant.isHurt = True

        for ant, toX, toY in toMove:
            self.isAnt[ant.x][ant.y] = False
            ant.x, ant.y = toX, toY



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
                       (+1, -1), (+1, +2), (+2, +0), (+2, +0) ]

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
        rRes = [(x, y, world.isRes[self.x+x][self.y+y]) for x,y in self.around]

        return rRes, rPheros



class Ant:
    def __init__(self, posX, posY, nest, callback):
        self.run = callback
        self.nest = nest
        self.x = posX
        self.y = posY
        self.isHurt = False
        self.isCarrying = False

    def __bool__(self):
        return True

    def createInput(self, world):
        """ Crops map and selects pheromones to input
        """
        s = world.settings['viewDistance']
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
                    r[i][j] = world.map[self.x][self.y]
                    continue
                
                l = abs(i - hs) + abs(j - hs)
                u, v = float(i - hs) / l, float(j - hs) / l
                
                bla = False
                for k in range(l + 1):
                    tile = world.map[int(self.x + k*u)][int(self.y + k*v)]
                    if rMap[int(hsz + k*u)][int(hsz + k*v)] == ~access.UNKNOWN:
                        rMap[int(hsz + k*u)][int(hsz + k*v)] = access.UNKNOWN \
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
        return posX-self.x+posY-self.y < world.settings['pheroRange']-self.decay
