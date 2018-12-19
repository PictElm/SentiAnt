from sentiant import api as _


PH_SPAWN = 0
PH_TRAIL = [1, 2, 3]


def main(self, resources, pheroList):
    r = False

    if not 'antCount' in self.memory.keys():
        self.memory['antCount'] = 0

    #if self.memory['antCount'] == 1: return r

    for x, y, available in resources:
        if available:
            r = (x, y, antRandom)
            self.memory['antCount']+= 1
            break

    if not r:
        r = _.WAIT

    return r


def antRandom(self, view, pheroList):
    if not self.memory:
        self.memory['lastTrailPhIndex'] = -1
        for d, opp in [(_.NORTH, _.SOUTH), (_.SOUTH, _.NORTH), \
                       (_.EAST, _.WEAST), (_.WEAST, _.EAST)]:
            _.info(_.asString(d) + ": " + str(view.isAnt(_.asPosition(d))))
            if isinstance(view.isAnt(_.asPosition(d)), _.AQueen):
                self.memory['wasMovingAway'] = opp
                break
        _.info("wasMovingAway: " + _.asString(self.memory['wasMovingAway']), \
               end="\n\n")
        self.memory['postponnedAction'] = None

    if self.age == 0:
        return _.MOVE_TO & self.memory['wasMovingAway'], PH_SPAWN

    action = _.WAIT
    direction = None
    phero = _.REFRESH_PHERO

    if self.memory['postponnedAction']:
        action = correctMoveTo(self, view,
                               _.asDirection(self.memory['postponnedAction']))
        self.memory['postponnedAction'] = None
        return action, phero

    ph_spawn = []
    ph_trail = []
    onPos = None

    for p in pheroList:
        if (p.x, p.y) == (0, 0):
            onPos = p
        if p.value == PH_SPAWN:
            ph_spawn.append(p)
        elif p.value in PH_TRAIL:
            ph_trail.append(p)

    moveToPh = None

    if view[0, 0] & _.RESOURCE and not (onPos and onPos.value == PH_SPAWN):
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
        direction = self.memory['wasMovingAway'] #if ph_spawn \
                   #else [_.NORTH, _.SOUTH, _.EAST, _.WEAST][_.RNG.randrange(4)]

        if not onPos:
            self.memory['lastTrailPhIndex']+= 1
            self.memory['lastTrailPhIndex']%= len(PH_TRAIL)
            phero = PH_TRAIL[self.memory['lastTrailPhIndex']]

    if moveToPh:
        if moveToPh.x < moveToPh.y:
            direction = _.NORTH if 0 < moveToPh.y else _.SOUTH
        else:
            direction = _.EAST if 0 < moveToPh.x else _.WEAST

    if direction:
        action = correctMoveTo(self, view, direction)

    if self.isCarrying and not action & _.MOVE_TO:
        self.memory['postponnedAction'] = action
        action = _.DROP_RES

    return action, phero


def correctMoveTo(ant, view, direction=None):
    action = _.MOVE_TO
    if not direction:
        direction = [_.NORTH, _.SOUTH, _.EAST, _.WEAST][_.RNG.randrange(4)]
    targeted = _.asPosition(direction)

    if view[targeted] & _.ROCK:
        ant.memory['postponnedAction'] = action | direction
        if direction in (_.NORTH, _.SOUTH):
            direction = [_.EAST, _.WEAST][_.RNG.randrange(2)]
        elif direction in (_.EAST, _.WEAST):
            direction = [_.NORTH, _.SOUTH][_.RNG.randrange(2)]

    isWall = view[targeted] & _.WALL
    isAnt = view.isAnt(targeted)

    if isinstance(isAnt, _.AAnt) and isAnt.color != ant.color:
        action = _.ATTACK_ON | direction
    else:
        action = (_.DIG_AT if isWall else _.MOVE_TO) | direction

    return action
