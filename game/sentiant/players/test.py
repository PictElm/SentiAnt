from sentiant import api as _


def main(self, resources, pheromonesList):
    r = False

    if not 'antCount' in self.memory.keys():
        self.memory['antCount'] = 0

    for x, y, available in resources:
        if available:
            r = (x, y, antRandom)
            self.memory['antCount']+= 1
            break

    if not r:
        r = _.WAIT

    return r


def antRandom(self, view, pheromonesList):
    action = _.WAIT

    if view[0, 0] & _.RESOURCE and not self.isCarrying:
        action = _.TAKE_RES
    else:
        action = chooseNextMoveTo(self, view)

    phero = _.KEEP_PHERO

    if self.age == 0:
        phero = 0

    for ph in pheromonesList:
        if ph.x == 0 and ph.y == 0 and ph.value == 0:
            phero = _.REFRESH_PHERO

            if self.isCarrying and not view[0, 0] & _.RESOURCE:
                action = _.DROP_RES
            elif not self.isCarrying:
                action = chooseNextMoveTo(self, view)

    return action, phero


def chooseNextMoveTo(ant, view):
    action = _.WAIT
    direction = [_.NORTH, _.SOUTH, _.EAST, _.WEAST][_.RNG.randrange(4)]
    targeted = _.asPosition(direction)

    isWall = view[targeted] & _.WALL
    isAnt = view.isAnt(targeted)

    if isAnt and isAnt.color != ant.color:
        action = _.ATTACK_ON | direction
    else:
        action = (_.DIG_AT if isWall else _.MOVE_TO) | direction

    return action
