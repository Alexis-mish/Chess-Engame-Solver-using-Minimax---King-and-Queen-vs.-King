# Queen and King vs. King Chess Endgame Solver

An AI-powered chess engine focused on solving the **King and Queen vs. King** endgame (White's side) using the **Minimax algorithm with Alpha-Beta Pruning** and a **Zobrist Hashing-based Transposition Table** for decisive, forced mate calculation.

The project is built using **Pygame** to provide a simple, interactive graphical interface, allowing a human player to control the solo Black King against the advanced computer opponent.

## Features

* **Decisive AI:** Implements a Minimax search to find the optimal move, aiming for the fastest forced checkmate against the solo Black King.
* **Performance Optimization:** Utilizes **Alpha-Beta Pruning** to significantly reduce the search space and a **Transposition Table** powered by **Zobrist Hashing** to store and reuse results from previously evaluated positions.
* **Heuristic Evaluation:** A custom, endgame-specific evaluation function designed to prioritize king restriction, queen proximity, and forcing the opponent king to the board edges.
* **Interactive GUI:** A simple and clean Pygame interface where the human player moves the Black King and observes the AI's moves.
* **Game State Detection:** Correctly identifies Checkmate and Stalemate conditions.

## Installation and Setup

### Prerequisites

You must have **Python 3.x** and the **Pygame** library installed.

pip install pygame


### Running the Game

1.  Clone the repository:

    git clone [https://github.com/Alexis-mish/Chess-Engame-Solver-using-Minimax---King-and-Queen-vs.-King.git](https://github.com/Alexis-mish/Chess-Engame-Solver-using-Minimax---King-and-Queen-vs.-King.git)
    cd Chess-Engame-Solver-using-Minimax---King-and-Queen-vs.-King

2.  Run the main script (assuming the file is named `chess_game.py`):

    python chess_game.py


## AI Engine Architecture

The core of this project is the Minimax search algorithm, optimized for finding the guaranteed win in this specific endgame.

-----

### Minimax with Alpha-Beta Pruning

The AI uses the **Minimax algorithm** to explore the game tree. As White is guaranteed a win in the K+Q vs. K endgame, the search aims to maximize the evaluation score.

  * **Maximizing Player (White):** Seeks the move that leads to the highest possible score (checkmate).
  * **Minimizing Player (Black):** Assumes the human player will always make the best possible move to delay the checkmate (minimizes White's score).

The $\alpha-\beta$ pruning technique is implemented to ensure that branches of the game tree that cannot affect the final decision are skipped, significantly enhancing search speed.

-----

### Transposition Table & Zobrist Hashing

To prevent re-calculating the value of board positions reached via different move orders, a **Transposition Table (TT)** is used.

  * **Zobrist Hashing:** A fast, probabilistic method generates a unique 64-bit integer (**hash key**) for every board state. This key is used for rapid lookup in the TT.
  * **Table Entry:** Each TT entry stores the calculated **score**, the search **depth** completed, and a flag (`TT_ALPHA`, `TT_BETA`, `TT_EXACT`) to correctly interpret the stored value during the $\alpha-\beta$ search, which is crucial for maximizing the efficiency of cutoffs.

-----

### Evaluation Function (`evaluate(board)`)

The evaluation function is tailored to measure progress toward the forced checkmate pattern. The score is based on the following weighted factors:

1.  **Checkmate/Stalemate:** Immediate termination values (1000 for mate, 0 for stalemate).
2.  **Black King Mobility:** Penalizes the Black King based on the count of legal moves available.
3.  **Distance to Corner:** Rewards White as the Black King is forced toward the board edges, where it is easier to mate.
4.  **Proximity of White Pieces:** Rewards the White Queen and White King for closing in on the Black King.
5.  **Check Bonus:** A substantial bonus if the Black King is currently in check.

## Usage Notes

  * **Restart:** Press the **'R'** key at any time to reset the board and start a new game.
  * **Threaded AI:** The computer's move calculation runs in a separate thread to prevent the Pygame window from becoming unresponsive during the Minimax search.
  * **Difficulty:** The constant `SEARCH_DEPTH` in the `computer_move` function dictates the AI's lookahead. Increasing this value will result in a stronger, though slower, AI.


```
```
