## Introduction

This memo gathers new ideas for a increasing the speed of the AI.

## Principles

* As much as possible `numpy` arrays have to be used instead of `Python` lists or dictionaries.
* The list of valid moves has to be implemented as a `Python generator`.
* No double validation: 
  * A move going to be played is always selected from a list of valid moves. This mist might be incomplete, however, for example for AI search purpose, or just for test purpose.
  * The execution of a valid move is just superficially checked.

