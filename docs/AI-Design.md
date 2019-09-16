#  AI-Design

## Command line interface

| Command                | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| **`era`**              | enable red algorithm                                         |
| **`eba`**              | enable blue algorithm                                        |
| **`dra`**              | disable red algorithm                                        |
| **`dba`**              | disable blue algorithm                                       |
| **`cra algo`**         | change red algorithm; example **`cra certu`**                |
| **`cba algo`**         | change blue algorithm                                        |
| **`sra option=value`** | set red algorithm; example **`sra depth=3`**                 |
| **`sba option=value`** | set blue algorithm                                           |
| **`aa`**               | ask algorithm for the current color                          |
| **`ram`**              | resume algorithm match (red algorithm versus blue algorithm) |
| **`pam moves`**        | pause algorithm match after the given moves                  |

## Relationship with the other classes

* At start, once, Runner creates the "certu" algorithm for each color.
* Both algorithms are disabled.
* At each iteration, Runner asks Game for the current color and if the game is over.
* If the game is not over and the color algorithm is enabled:
  * Runner sets the color algorithm with a copy of Game.
  * Runner asks the algorithm for its advised move.
  * The algorithm returns the  advised move as a string.
  * Runner uses the return string instead of the human input.
* When both red and blue algorithms are enabled, Runner chains them until
  a limit is reached. The user has to enter `ram` to resume the chaining.

