# Imports every usefull functions and constants.
from sentiant import api as _


def main(self, resources, pheromonesList):
    """ This `main` function is mandatory: that's the function
        your queen will be running on.

        ## Arguments:
        + `queen`: an instance of `access.AQueen`;
        + `resources`: a list of `(x, y, available)` where `available` is
            `True` if there is a usable resource on the tile at `(x, y)`
            relative to the queen;
        + `pheromonesList`: a list of `APhero` spotted from any of the 4
            tiles the queen occupies.

        ## Returns:
        You can return a `(x, y, callback)` where `(x, y)` the are coordinate
        of a usable resource relative to the queen and `callback` is a function
        an ant can use (see bellow); this will cause the resource to be
        replaced be an new ant which `run` function is `callback`.
        Anything else won't be processed. Prefer using `access.WAIT` to idle.
    """
    r = False

    if not 'antCount' in self.memory.keys():
        self.memory['antCount'] = 0

    # Starting sequences can facilitate debugging.
    mainseq = _.seqstart(self.color + ".main")

    _.info("trying to spawn an `antRandom` somewhere...")

    for x, y, available in resources:
        if available:
            # We found a usable resource!
            _.debug("selected resource at {}, {} from me".format(x, y))
            # The new ant will use the algorithm described below.
            r = (x, y, antRandom)
            # Keep track of the number of ants spawned from the beginning.
            self.memory['antCount']+= 1
            break

    if not r:
        # Oops! We didn't find anything... Let's throw a warning!
        _.warning("404 - resource not found!")
        r = _.WAIT

    # Ending our main sequence...
    _.seqend(mainseq)
    return r


def antRandom(self, view, pheromonesList):
    """ This is a simple example of function in compliance with what an ant
        needs to run.

        ## Arguments:
        + `self`: a `access.AAnt` instance;
        + `view`: a part of the world maps, of size `settings: viewDistance`
            centered on the ant (this is an instance of `access.AView`);
        + `pheromonesList`: a list of `APhero` spotted from the tiles the
            ant occupies.

        ## Returns:
        For any of the 3 following actions, `direction` should take only one
        value from `access.NORTH`, `access.SOUTH`, `access.EAST` or
        `access.WEAST`:

        + move to a tile: `access.MOVE_TO | direction`;
        + dig a wall: `access.DIG_AT | direction`;
        + attack an adjacent ant: `access.ATTACK_ON | direction`.

        As the 3 following actions take place on the same tile as the ant, no
        direction is required:

        + drop a resource on the ground (if carrying): `access.DROP_RES`;
        + pick up a resource on the ground (if not): `access.TAKE_RES`;
        + do nothing: `access.WAIT` (or anything unexpected -- again, prefer
            using `access.WAIT` to idle).
    """
    #_.debug("What do I do" + (" with this!?" if self.isCarrying else "?!"))

    action = _.WAIT

    # If there is a resource on the ground and we are not carrying one, ..
    if view[0, 0] & _.RESOURCE and not self.isCarrying:
        # .. we take it!
        action = _.TAKE_RES
    else:
        # .. otherwise, we move somewhere randomly...
        action = chooseNextMoveTo(self, view)

    # This is to not affect a pheromone that would be on our tile.
    phero = _.KEEP_PHERO

    # Let's say we use the pheromone 0 to locate the spawn points.
    if self.age == 0:
        _.debug("Marking spawn...")
        phero = 0

    for ph in pheromonesList:
        # If the pheromone on our tile indicate a spawn point, ..
        if ph.x == 0 and ph.y == 0 and ph.value == 0:
            # .. we refresh it.
            _.debug("Refreshing spawn indicator...")
            phero = _.REFRESH_PHERO

            # We may as well try to replenish the stocks.
            if self.isCarrying and not view[0, 0] & _.RESOURCE:
                _.info("There! I got you a cookie!")
                action = _.DROP_RES
            # Don't pick up the resource on the verry next turn!
            elif not self.isCarrying:
                action = chooseNextMoveTo(self, view)

    # Note that the pheromone part will take place before the action part.
    #_.debug(describeIntents(action, phero))
    return action, phero


def chooseNextMoveTo(ant, view):
    """ ## You can define and use your own function:
        This function choose a random adjacent tile to move to; if the tile is
        blocked, dig through, if the tile is allready occupied by other than an
        ally ant, **kill it**.
    """
    action = _.WAIT
    direction = [_.NORTH, _.SOUTH, _.EAST, _.WEAST][_.RNG.randrange(4)]
    targeted = _.asPosition(direction)

    # If we cant move there because of a wall or an ant, we waste the turn!
    isWall = view[targeted] & _.WALL
    isAnt = view.isAnt(targeted)

    if isAnt and isAnt.color != ant.color:
        action = _.ATTACK_ON | direction
    else:
        action = (_.DIG_AT if isWall else _.MOVE_TO) | direction

    return action


def describeIntents(action, phero):
    AtoS = ""

    if action & _.MOVE_TO:
        AtoS = "move to "
    elif action & _.ATTACK_ON:
        AtoS = "attack on "
    elif action & _.DIG_AT:
        AtoS = "dig at "
    elif action & _.WAIT:
        AtoS = "wait "

    if action & _.NORTH:
        AtoS+= "north"
    elif action & _.SOUTH:
        AtoS+= "south"
    elif action & _.EAST:
        AtoS+= "east"
    elif action & _.WEAST:
        AtoS+= "weast"

    PtoS = ""

    if phero & _.KEEP_PHERO:
        PtoS = "keep this pheromone as it is"
    elif phero & _.REFRESH_PHERO:
        PtoS = "refresh this pheromone"
    elif phero in range(16):
        PtoS = "apply a " + str(phero) + " pheromone"

    return "I will " + AtoS + " after I've " + PtoS + "."
