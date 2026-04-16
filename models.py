# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the Tic Tac Toe Environment.

The tic_tac_toe environment is a simple test environment that echoes back messages.
"""

import typing
from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class TicTacToeAction(Action):
    """Action for the Tic Tac Toe environment."""

    position: int = Field(..., description="Position to place the mark (0-8 in row-major order).")


class TicTacToeObservation(Observation):
    """Observation from the Tic Tac Toe environment."""

    board: typing.List[str] = Field(description="The 9-element string list representing the board state.")
    current_player: str = Field(description="The player whose turn it is ('X' or 'O').")
    winner: typing.Optional[str] = Field(default=None, description="Winner of the game, or None.")
    is_tie: bool = Field(default=False, description="True if the game is a tie.")
    invalid_move: bool = Field(default=False, description="True if the last action was an invalid move.")
