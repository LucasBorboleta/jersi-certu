# jersi certu

The Python 3 package *jersi_certu* provides a GUI and a rules engine for playing the *jersi* board-game version 4 and also for testing AI agents. 

Below is an overview of the GUI interface, which retrieves the human chosen action thanks to a text field. It is simple and straightforward. The intent has been to focus on the rules engine, the generator of all possible actions (for AI purpose) and the graphical display. Minimal time was spent on graphical input.  

All combinations of players are possible: human/human, human/AI, AI/human and AI/AI. Current AI agents are: purely random (mainly used for tests) and MCTS (Monte Carlo Tree Search). MCTS agents are parametrized in seconds or in iterations. The branching ratio of *jersi* is pretty high (often greater than 100 or even 1000 when drops are still possible), so MCTS (with a simple random roll-out policy) poorly performs. An experimental biased roll-out policy, nammed *jrp*, is provided.

The name of the package is coined after *certu* which means *expert* in lojban conlang.

If you intent to derive or to sell either a text, a product or a software from this work, then read the [**LICENSE**](./docs/LICENSE.txt) and the  [**COPYRIGHT**](./docs/COPYRIGHT.md)  documents.

![](./docs/jersi-scene.png)
