import api.access as _

def main(queen, ressourceAvailables, pheromonesList):
    r = False
    _.seqstart(queen.color + ".main")

    _.info("trying to spawn an `antRandom` somewhere...")

    for x, y, available in ressourceAvailables:
        if available:
            _.debug("selected resource at {}, {} from me".format(x, y))
            r = (x, y, antRandom)
            break

    if not r:
        _.warning("404 - resource not found!")
        r = _.WAIT

    _.seqend()
    return r

def antRandom(self, view, pheromonesList):
    _.debug("What do I do!?")

    action = _.WAIT

    if _.RES_ON_TILE & view[0, 0] and not self.isCarrying:
        action = _.TAKE_RES
    else:
        direction = [_.NORTH, _.SOUTH, _.EAST, _.WEAST][_.RNG.randrange(4)]
        action = _.MOVE_TO | direction

    phero = _.KEEP_PHERO

    return action, phero
