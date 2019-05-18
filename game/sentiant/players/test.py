from sentiant import api as _


PH_SPAWN = 0
PH_TRAIL = { _.NORTH: 1, _.SOUTH: 2, _.EAST: 3, _.WEAST: 4 } # indicate home

DIR = [_.NORTH, _.SOUTH, _.EAST, _.WEAST]
DIR_PRP = { _.NORTH: [_.EAST, _.WEAST], _.SOUTH: [_.EAST, _.WEAST], \
             _.EAST: [_.NORTH, _.SOUTH], _.WEAST: [_.NORTH, _.SOUTH] }
DIR_OPP = { _.NORTH: _.SOUTH, _.SOUTH: _.NORTH, \
            _.EAST: _.WEAST, _.WEAST: _.EAST }

def main_lock(self, resources, pheroList):
    r = False

    if not 'antCount' in self.memory.keys():
        self.memory['antCount'] = 0

    #if self.memory['antCount'] == 1: return r

    for x, y, available in resources:
        if available:
            r = (x, y, testAnt)
            self.memory['antCount']+= 1
            break

    if not r:
        r = _.WAIT

    return r


def testAnt(self, view, pheroList):
    if not self.memory:
        self.memory['direction'] = DIR_OPP[dirOfNearby(0, 0, view, _.AQueen)]
        self.memory['postponed'] = None, _.KEEP_PHERO

    if self.age == 0:
        return _.WAIT, PH_SPAWN

    direction = self.memory['direction']
    action, phero = self.memory['postponed']

    if action:
        self.memory['postpone'] = None, _.KEEP_PHERO
        if not isUseless(action, view):
            return action, phero

    phOnPos = None
    for p in pheroList:
        if (p.x, p.y) == (0, 0):
            onPos = p
        if p.value == PH_SPAWN:
            ph_spawn.append(p)
        elif p.value in PH_TRAIL:
            ph_trail.append(p)

    moveToPh = None

    if view[0, 0] & _.RESOURCE and not self.isCarrying \
       and not (onPos and onPos.value == PH_SPAWN):
        action = _.TAKE_RES

    elif self.isCarrying:
        if onPos and onPos.value == PH_SPAWN:
            action = _.DROP_RES

        elif ph_spawn:
            moveToPh = ph_spawn[0]
            for p in ph_spawn[1:]:
                if p.x + p.y < moveToPh.x + moveToPh.y:
                    moveToPh = p

        elif ph_trail:
            if onPos and onPos.value in PH_TRAIL: # 1->3->2->1
                seeks = PH_TRAIL[onPos.value - 2]
                moveToPh = ph_trail[0]
                for p in ph_trail[1:]:
                    if p.x + p.y < moveToPh.x + moveToPh.y and p.value == seeks:
                        moveToPh = p
            else:
                moveToPh = ph_trail[0]
                for p in ph_trail[1:]:
                    if p.x + p.y < moveToPh.x + moveToPh.y:
                        moveToPh = p

    else: # not carrying
        if ph_spawn:
            direction = self.memory['wasMovingAway']
        else:
            choices = [_.NORTH, _.SOUTH, _.EAST, _.WEAST]
            choices.remove({ _.NORTH: _.SOUTH, \
                             _.SOUTH: _.NORTH, \
                             _.EAST: _.WEAST, \
                             _.WEAST: _.EAST }[self.memory['wasMovingAway']])
            direction = choices[_.RNG.randrange(len(choices))]

        if not onPos or onPos.value != PH_SPAWN:
            self.memory['lastTrailPhIndex']+= 1
            self.memory['lastTrailPhIndex']%= len(PH_TRAIL)
            phero = PH_TRAIL[self.memory['lastTrailPhIndex']]

    if moveToPh:
        if moveToPh.x < moveToPh.y:
            direction = _.NORTH if 0 < moveToPh.y else _.SOUTH
        else:
            direction = _.EAST if 0 < moveToPh.x else _.WEAST

    if direction:
        action = correctMoveTo(self, view, phero, phOnPos,pheroList, direction)

    if self.isCarrying and not action & _.MOVE_TO:
        self.memory['postponnedAction'] = action
        action = _.DROP_RES

    return action, phero


def correctMoveTo(self, view, phero, phOnPos, pheroList, direction=None):
    action = _.MOVE_TO
    if not direction:
        direction = [_.NORTH, _.SOUTH, _.EAST, _.WEAST][_.RNG.randrange(4)]
    targeted = _.asPosition(direction)

    if view[targeted] & _.ROCK:
        self.memory['postponnedAction'] = action | direction
        if direction in (_.NORTH, _.SOUTH):
            direction = [_.EAST, _.WEAST][_.RNG.randrange(2)]
        elif direction in (_.EAST, _.WEAST):
            direction = [_.NORTH, _.SOUTH][_.RNG.randrange(2)]

    if self.isCarrying:
        if phOnPos:
            # drop res on spawn points
            if phOnPos.value == PH_SPAWN:
                return _.DROP_RES, _.REFRESH_PHERO
            # follow trail back home
            elif phOnPos.value in PH_TRAIL.values():
                for k, v in PH_TRAIL.items():
                    if v == phOnPos.value:
                        direction = k
                action = correctDir(self, direction, view)
                self.memory['direction'] = _.asDirection(action)
                if not action & _.MOVE_TO:
                    self.memory['postponed'] = action, phero
                    return _.DROP_RES, _.KEEP_PHERO
                return action, _.KEEP_PHERO

        # no phero on pos
        else:
            return _.MOVE_TO | self.memory['direction'], _.KEEP_PHERO
            # look for nearby trail to get back on
            dest = None
            for p in pheroList:
                if p.value in PH_TRAIL.values():
                    if dest and p.x + p.y < dest.x + dest.y or not dest:
                        dest = p
            # if trail nearby found
            if dest:
                # move y, if blocked move x, if blocked postpone movement
                direction = _.NORTH if 0 < dest.y else _.SOUTH
                if view[_.asPosition(direction)] & (_.ROCK | _.WALL):
                    direction = _.EAST if 0 < dest.x else _.WEAST
                action = correctDir(self, direction, view)
                if not action & _.MOVE_TO:
                    self.memory['postponed'] = action, phero
                return _.DROP_RES, _.KEEP_PHERO
            # no trail markers found, move randomly somewhere dug
            else:
                all = DIR.copy()
                _.RNG.shuffle(all)
                for d in all:
                    if not view[_.asPosition(d)] & (_.ROCK | _.WALL):
                        return d, _.KEEP_PHERO

    # not carrying res
    else:
        if phOnPos and phOnPos.value == PH_SPAWN:
            direction = DIR_OPP[dirOfNearby(0, 0, view, _.AQueen)]
            self.memory['direction'] = direction
            return _.MOVE_TO | direction, _.KEEP_PHERO

        elif view[0, 0] & _.RESOURCE:
            return _.TAKE_RES, PH_TRAIL[DIR_OPP[self.memory['direction']]]

        # keep moving towards direction from memory
        else:
            action = correctDir(self, self.memory['direction'], view)
            direction = _.asDirection(action)
            phero = _.KEEP_PHERO
            # if direction changes (obstacles) continu the trail
            if self.memory['direction'] != direction:
                phero = PH_TRAIL[DIR_OPP[self.memory['direction']]]
                self.memory['direction'] = direction
            return action, phero

    return correctDir(self, DIR[_.RNG.randrange(4)], view), _.KEEP_PHERO


def dirOfNearby(x, y, view, c=_.AQueen):
    for d in DIR:
        dx, dy = _.asPosition(d)
        if isinstance(view.isAnt(x+dx, y+dy), c):
            return d

def correctDir(ant, direction, view):
    tile = view[_.asPosition(direction)]
    isAnt = view.isAnt(_.asPosition(direction))

    if tile & _.ROCK:
        all = DIR_PRP[direction] + [DIR_OPP[direction]]
        for d in all:
            p = _.asPosition(d)
            if not view[p] and not view.isAnt(p):
                return correctDir(ant, d, view)
        return _.WAIT | direction
        #return correctDir(ant, DIR_PRP[direction][_.RNG.randrange(2)], view)

    if tile & _.WALL:
        return _.DIG_AT | direction

    if isAnt and isinstance(isAnt, _.AAnt):
        if isAnt.color != ant.color:
            return _.ATTACK_ON | direction
        else:
            all = DIR.copy()
            for d in all:
                p = _.asPosition(d)
                if not view[p] and not view.isAnt(p):
                    return correctDir(ant, d, view)
            return _.WAIT | direction

    return _.MOVE_TO | direction

def isUseless(action, view):
    pos = _.asPosition(action)
    return action & _.ATTACK_ON and not view.isAnt(pos) or \
           action & _.DIG_AT and (not view[pos] & _.WALL or view[pos] & _.ROCK)
