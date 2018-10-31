import api.access as _

def main(queen, resources, pheromonesList):
    """ This `main` function is mandatory: that's the function
        your queen will be running on.

        ## Arguments:
        + `queen`: an instance of `access.AQueen`;
        + `resources`: a list of `(x, y, available)` where `available` is
            `True` if there is a usable resource on the tile at `(x, y)`
            relative to the queen;
        + `pheromonesList`: a list of `APhero` spoted from any of the 4
            tiles the queen occupies.

        ## Returns:
        You can return a `(x, y, callback)` where `(x, y)` the are coordinate
        of a usable resource relative to the queen and `callback` is a function
        an ant can use (see bellow); this will cause the resource to be
        replaced be an new ant which `run` function is `callback`.
        Anything else won't be processed. Prefer using `access.WAIT` to idle.
    """
    r = False

    # Starting sequences can facilitate debugging.
    mainseq = _.seqstart(queen.color + ".main")

    _.info("trying to spawn an `antRandom` somewhere...")

    for x, y, available in ressources:
        if available:
            # We found a usable resource!
            _.debug("selected resource at {}, {} from me".format(x, y))
            # The new ant will use the algorithm described below.
            r = (x, y, antRandom)
            break

    if not r:
        # Woops! We didn't found anything... Let's throw a warning.
        _.warning("404 - resource not found!")
        r = _.WAIT

    # Ending our main sequence...
    _.seqend(mainseq)
    return r

def antRandom(self, view, pheromonesList):
    """ This is a simple example of function in compliance with what an ant
        needs to run.

        ## Arguments:
        + self: a `access.AAnt` instance;
        + view: a part of the world maps, of size `settings: viewDistance`
            centred on the ant (this is an instance of `access.AView`);
        + `pheromonesList`: a list of `APhero` spoted from the tiles the
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

        + pick up a resource on the ground (if not carrying): `access.TAKE_RES`;
        + drop a resource on the ground (if carrying): `access.DROP_RES`;
        + do nothing: `access.WAIT` or anything invalid.
    """
    _.debug("What do I do" + "with this!?" if self.isCarrying else "?!")

    action = _.WAIT

    # If there is a resource on the ground and we are not carrying one, ..
    if _.RES_ON_TILE & view[0, 0] and not self.isCarrying:
        # .. we take it!
        action = _.TAKE_RES
    else:
        # .. otherwise, we move somwhere randomly...
        direction = [_.NORTH, _.SOUTH, _.EAST, _.WEAST][_.RNG.randrange(4)]
        # (note that if we cant move there because of a wall, we waste the turn
        #  doing nothing!)
        action = _.MOVE_TO | direction

    # This is to not affect a pheromone that would be on our tile.
    phero = _.KEEP_PHERO

    return action, phero
