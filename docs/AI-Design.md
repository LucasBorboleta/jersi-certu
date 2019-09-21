#  AI-Design

## Command line interface

| Command                    | Description                                                  |
| -------------------------- | ------------------------------------------------------------ |
| **`cba algo`**             | change blue algorithm ; example **`cba certu`**              |
| **`cra algo`**             | change red algorithm                                         |
| **`eba`**                  | enable blue algorithm                                        |
| **`era`**                  | enable red algorithm                                         |
| **`dba`**                  | disable blue algorithm                                       |
| **`dra`**                  | disable red algorithm                                        |
| **`pa`**                   | print algorithms (name, status, options)                     |
| **`paa`**                  | print available algorithms                                   |
| **`sba option=value ...`** | set blue algorithm with options                              |
| **`sra option=value ...`** | set red algorithm with options                               |
| **`aa`**                   | ask advice to the algorithm of the current color             |
| **`rea n`**                | repeat `n` times the blue-red algorithms, if they are both enabled |

## Relationship with the other classes

* At start, Runner creates an algorithm for each color. A default algorithm is used. Both created algorithms are disabled.
* At each iteration, Runner asks Game for the current color and if the game is over.
* If the game is not over and the current color algorithm is enabled:
  * Runner sets the color algorithm with a copy of Game.
  * Runner asks the algorithm for its advised move.
  * The algorithm returns the  advised move as a string.
  * Runner uses the return string instead of the human input.
* When both blue and red algorithms are enabled, the `rea n`command repeats `n` times the sequence blue-red algorithms.

