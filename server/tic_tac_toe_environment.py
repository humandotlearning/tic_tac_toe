# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Tic Tac Toe Environment Implementation.

A simple test environment that echoes back messages sent to it.
Perfect for testing HTTP server infrastructure.
"""

import random
import typing
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import TicTacToeAction, TicTacToeObservation
except ImportError:
    from models import TicTacToeAction, TicTacToeObservation


class TicTacToeEnvironment(Environment):
    """
    Tic Tac Toe Environment.
    
    A 2-player environment where players take alternating turns to place their 
    marks ('X' or 'O') on a 3x3 board. It evaluates valid moves and tracks win, 
    loss, and tie conditions automatically.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        """
        Initialize the tic_tac_toe environment.
        
        Sets up the initial network tracking state, initializes an empty 
        3x3 board, and randomly selects the starting player.
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0
        self._board = [" "] * 9
        self._current_player = random.choice(["X", "O"])

    def _check_winner(self) -> typing.Optional[str]:
        """
        Evaluate the current board for horizontal, vertical, or diagonal wins.

        Returns:
            The string mark of the winning player ('X' or 'O') if a win condition 
            is met. Otherwise, returns None.
        """
        winning_positions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # cols
            [0, 4, 8], [2, 4, 6]             # diagonals
        ]
        for p in winning_positions:
            if self._board[p[0]] != " " and self._board[p[0]] == self._board[p[1]] == self._board[p[2]]:
                return self._board[p[0]]
        return None

    def reset(self) -> TicTacToeObservation:
        """
        Reset the environment to a completely fresh game state.

        Returns:
            TicTacToeObservation containing the cleared board, the new randomly 
            chosen starting player, and reset status flags.
        """
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1
        
        self._board = [" "] * 9
        self._current_player = random.choice(["X", "O"])

        return TicTacToeObservation(
            board=self._board.copy(),
            current_player=self._current_player,
            winner=None,
            is_tie=False,
            invalid_move=False,
            done=False,
            reward=0.0,
        )

    def step(self, action: TicTacToeAction) -> TicTacToeObservation:  # type: ignore[override]
        """
        Execute a game step by placing the current player's mark at the specified position.
        
        Evaluates validity of the move, updates board state, and determines game over 
        conditions (like Win or Tie). The action inherently applies to `_current_player`.

        Args:
            action: A TicTacToeAction object containing the target `position` (0-8) 
                    to place the mark.

        Returns:
            TicTacToeObservation describing the new board state, who plays next, 
            the step's reward, and any flags denoting an invalid move, a tie, or a win.
        """
        self._state.step_count += 1
        pos = action.position

        # Check invalid move
        if pos < 0 or pos > 8 or self._board[pos] != " ":
            return TicTacToeObservation(
                board=self._board.copy(),
                current_player=self._current_player,
                winner=None,
                is_tie=False,
                invalid_move=True,
                done=False,
                reward=-1.0,
                metadata={"step": self._state.step_count, "error": "Invalid move"},
            )

        # Apply move
        self._board[pos] = self._current_player

        # Check win/tie
        winner = self._check_winner()
        is_tie = False
        done = False
        reward = 0.0

        if winner:
            done = True
            reward = 1.0
        elif " " not in self._board:
            is_tie = True
            done = True
            reward = 0.2
        else:
            # Change turn
            self._current_player = "O" if self._current_player == "X" else "X"

        return TicTacToeObservation(
            board=self._board.copy(),
            current_player=self._current_player,
            winner=winner,
            is_tie=is_tie,
            invalid_move=False,
            done=done,
            reward=reward,
            metadata={"step": self._state.step_count},
        )

    @property
    def state(self) -> State:
        """
        Get the current environment state.

        Returns:
            The current State object, which encapsulates the tracked episode_id 
            and the current step_count.
        """
        return self._state
