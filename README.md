# SentiAnt

## Overview

SentiAnt is a catch-the-flag game in which the player (maker / programmer / ..) conceives programs and assigns them to ants to maintain, defend and evolve an ant-hill in competition with another one.

---

## Beginning of the game

The map consists of a grid of N by N (more than 60 by 60) in which ants evolve. Each ant occupies one square and each square has only one ant.

The nests begins with only their respective queen (fixed unit occupying two cells allowing the production of mobile units) and 8 resources. Initially, the map is fully obstructed by walls "digable" (commun underground) or not (rocks), with the exception of the areas around each queens.

<img src="https://github.com/PictElm/SentiAnt/raw/master/images/example_queen.png" width="250">
In the center: a queen with 8 adjacent resources by default.

In the top left: 5 rocks that can not be dug through.

## End of the game

A flag is randomly placed on the map at the beginning of the game. The simulation ends when an ant places this flag next to a queen (in which case the queen's nest wins, so do not be miss your own queen!).

---

# Units (ants)

When the designer creates a mobile unit, he uses a resource and must assign his new ant an algorithm which inputs and outputs are described below.

Each of these ants receives, at the beginning of the calculation round, a grid of the 7 by 7 visible squares (or not, see example below), as well as the list of positions, relative to its own, of the pheromones on the map.

It can then at each turn, for one of the 4 adjacent tiles (N / S / E / W):
+ move to it if the tile is not a wall,
+ dig it if it’s one, and it’s not a rock (in which case it doesn’t move),
+ attack an adjacent ant;
For his own tile:
+ pick up a resource on the ground,
+ drop a resource on the ground.

Special case of the queen: she can use a resource located on an adjacent square to generate a new ant. This new unit appears on the same tile of the resource used.

Any of theses action ends its turn. Nevertheless, the ant can also place a pheromone on its place; this action can be performed at the same time as one of those above.
When the ant carries a resource, only the first and last option are available (moving and dropping).
All ants shares the same characteristics especially to attack and take hits: a unit is destroyed in 2 shots. A destroyed unit drops its resource if it was carrying one.

<img src="https://github.com/PictElm/SentiAnt/raw/master/images/example_random.png" width="250">
For example, in the following situation:
+ The shaded areas are not readable: they take the value 'UNKNOWN' if the algorithm tries to access them;
+ The ants can not dig to its right (E) because of the rock;
+ Bottom right is a pheromone (see below).

It can:
+ Dig in ahead (N) and on the left (W), it will stay on the same place;
+ Pick up the resource on its tile, except it will not be able to dig on the next turn;
+ Do nothing.

Whatever it does, it can also edit the value of the pheromone (see paragraph below) at its position.

---

## Resources

The ants can find resources, initially uniformly distributed over the map. When one of these resources is brought to the queen, she can use it to bring up a new unit. When the resource is used, it is returned randomly to the map. A tile can only accommodate one resource.

## Pheromones

Pheromones are stored as integers associated to a position in the grid. It can take a value from 0 to 15.
When an ant applies a pheromone to its position during its computation turn, any previous pheromone is totally overridden.
The odor released by a pheromone have an initial range of 5 cells: below is represented a pheromone which has lost 2 rank in range. The smell carries beyond walls and rocks. A pheromone disappears gradually each time an ant passes over it and its range decreases by 1 rank.

When an ant is in range of a pheromone (green zone), it is added to the list of perceived pheromones.

This list contains the integer identifying the pheromone itself, as well as its position, relative to the ant that perceives it. It is part of the input parameters of the ant algorithm.

<img src="https://github.com/PictElm/SentiAnt/raw/master/images/example_pheromone.png" width="250">
(The scope of the smell of the pheromone in the center has decreased by 2: where it is, the ant can not detect it.)

---

## Introduction to `access.py`

404 - not done yet :)
