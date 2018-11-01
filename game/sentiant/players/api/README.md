## An `Ant`



## The `Queen` and the `main`

The `Queen` is a special static unit used to produce units: therefore its only output available are `access.WAIT` or `(x, y, cb)` to spawn a new ant.

The `run` callback function of a `Queen` is loaded from the file you provided: it's the mandatory `main` function. Its inputs are:

+ A list of tuples `(x, y, b)` where `x` and `y` are coordinate relative to the queen's lower position, and `b` is a boolean indicating whether there is a resources on the tile.
+ The same list of pheromones as any normal ants, except the queen cant sent from all of the 4 case it occupies.

In the `world`'s `tick` function, all queen's `run` are called before any ant move.

In order to spawn a new ant, return the relatives coordinate of the selected resource around it (from the given position list), along with the callback function to associate with the new unit.