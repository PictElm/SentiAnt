# Introduction

This game is made to be understandable by only looking at the `example.py` and trying to edit it. Although if you still miss some details, you can read this file or any parts of the (not commented) game's code.

The only part of the game's files you may want to understand is the `access.py`: it contains everything you can use in your algorithms. In fact, **you should at no point _need_ any other elements**, other than the content from `access.py` along with any inputs given to your functions.

## TL;DR

Your file have a `main` function, `Queen` executes this function with for inputs: **itself**, **resources around** and **pheromones detected**. If you return coordinates from the **resources around** argument along with a **call-back function**, you can create an `Ant`. This newly created ant will, as any previous, use its attributed **call-back function** with for inputs: **itself**, **its view** and **pheromones detected**. You may return an **action** and a **pheromone**.

You may also want to know that `NORTH` is `(x, y + 1)` and `EAST` is `(x + 1, y)`.
If you've fully understood, the following can be repetitive.

## Running a simulation

### using a seed


# What do I do?

## Actions

Each time an ant's `run` function is called, it expect to get an ***action*** as return. ***Actions** are combination of flags that will be processed to execute the move you've planed for the ant.

### directional actions

+ `MOVE_TO` to move to another tile;
+ `DIG_AT` to dig an adjacent wall;
+ `ATTACK_ON` to attack that ant next to your's.

Using a **directional actions** requires you to give a **direction** in `NORTH`, `SOUTH`, `EAST` and `WEAST`. If your thinking from the `(x, y)` coordinates:

+ `NORTH` is `(x, y + 1)`
+ `SOUTH` is `(x, y - 1)`
+ `EAST` is `(x + 1, y)`
+ `WEAST` is `(x - 1, y)`

### on-tile actions

+ `TAKE_RES` to take a resource lying on your tile;
+ `DROP_RES` to let go of a carried resource;
+ `WAIT` to win immediately (what do _you_ think this will do?).

## Pheromones

### normal cases

### special cases


# What is out there?

## The game's entities

### the `Ant` kind

`Ant`s are the only kind of units, in that all `Ant`s spawned share the same characteristics.

When you create an `Ant`, you must supply a call-back `run` function with for inputs:

+ An `AAnt` object: this is a class wrapper design to allow you access to properties of you ant, but at the same time to prevent you from affecting their values.
+ The field of view of your ant as a grid, or rather an `AView` object, which size is defined in the settings.
+ The list of all `Phero` detected from your position in the world, wrapped into `APhero` object.

### the `Queen` and its `main`

The `Queen` is a special static unit used to produce units: therefore its only output available are `access.WAIT` or `(x, y, callback)` to spawn a new ant following `callback`'s algorithm.

The `run` call-back function of a `Queen` is loaded from the file you provided: it's the mandatory `main` function. Its inputs are:

+ An `AQueen` object, in the same idea as `AAnt`.
+ A list of tuples `(x, y, available)` where `x` and `y` are coordinate relative to the queen's lower position, and `available` is a boolean indicating whether there is a resources on the tile.
+ The same list of pheromones as any normal ants, except the queen cant sent from all of the 4 case it occupies.

In the `world.tick` function, all queen's `run` are called before any ant move.

In order to spawn a new ant, return the relatives coordinate of the selected resource around it (from the given position list), along with the call-back function to associate with the new unit.

### the `Phero`s

