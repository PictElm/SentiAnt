import sentiant.players.api.access as access
import sentiant.graph as graph


class World:
    def __init__(self, configFile="sentiant/settings.config"):
        self.settings = {}

        for it in open(configFile).readlines():
            k, v = it.strip().replace(' ', '').split(':')
            self.settings.update({ k: int(v) if v.isnumeric() else v })
        access.settings.update(self.settings)

        self.nests = []
        self.pheros = []

        s = self.settings['worldSize']
        self.antT = [[False for k in range(s)] for k in range(s)]
        self.resT = [[False for k in range(s)] for k in range(s)]
        self.mapT = [[access.WALL for k in range(s)] for k in range(s)]

        r = self.settings['rocksPercent']
        for k in range(int(s * s * r / 100)):
            self[self.mapT, access.RNG.randrange(s), access.RNG.randrange(s)]

        a = self.settings['resAmount']
        for k in range(a):
            i, j = access.RNG.randrange(s), access.RNG.randrange(s)
            while self[self.resT, i, j]:
                i, j = access.RNG.randrange(s), access.RNG.randrange(s)
            self[self.resT, i, j]

    def addNest(self, nest):
        for i in range(-3, 5):
            for j in range(-3, 5):
                if abs(i-1) + abs(j-1) < 5:
                    self[self.mapT, nest.queen.x + i, nest.queen.y + j] = access.EMPTY

        for i, j in nest.queen.around:
            self[self.resT, nest.queen.x + i, nest.queen.y + j] = True

        self.nests.append(nest)

    def getAntByPos(self, x, y):
        return self[self.antT, x, y]

    def coords(self, x, y):
        s = self.settings['worldSize']
        if not x in range(s) or not y in range(s):
            return x % s, y % s
        return x, y

    def __setitem__(self, Txy, v):
        T, x, y = Txy
        x, y = self.coords(x, y)
        T[x][y] = v

        flags = graph.EMPTY

        flags|= graph.ANT if self.antT[x][y] else 0
        flags|= graph.RES if self.resT[x][y] else 0
        flags|= graph.WALL if self.mapT[x][y] & access.WALL else 0
        flags|= graph.ROCK if not self.mapT[x][y] & access.DIGGABLE else 0

        graph.updateTile(x, y, flags)

    def __getitem__(self, Txy):
        T, x, y = Txy
        x, y = self.coords(x, y)
        return T[x][y]

    def turn(self):
        for nest in self.nests:
            queen = nest.queen
            resPos, pheros = queen.createInput(self)
            action = queen.run(access.AQueen(queen), resPos, pheros)

            if action != access.WAIT:
                posX, posY, cb = action

                if self[self.resT, posX, posY] == False:
                    nest.ants.append(Ant(posX, posY, nest, cb))
                    self[self.resT, posX, posY] = False
                    self[self.antT, posX, posY] = True

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
                    
                if dest and not self[self.antT, dest[0], dest[1]] \
                   and not self[self.mapT, dest[0], dest[1]] & WALL:
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

                if dest and self[self.mapT, dest[0], dest[1]] & access.DIGGABLE \
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
