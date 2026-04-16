import time
import subprocess
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from tic_tac_toe.client import TicTacToeEnv
    from tic_tac_toe.models import TicTacToeAction
except ImportError:
    from client import TicTacToeEnv
    from models import TicTacToeAction

def print_board(board):
    print("\n")
    print(f" {board[0]} | {board[1]} | {board[2]} ")
    print("---+---+---")
    print(f" {board[3]} | {board[4]} | {board[5]} ")
    print("---+---+---")
    print(f" {board[6]} | {board[7]} | {board[8]} ")
    print("\n")

def main():
    print("Starting server in the background...")
    # Start the server
    server_process = subprocess.Popen(["uv", "run", "python", "-m", "server.app", "--port", "8000"])
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Connect client to the server
        with TicTacToeEnv(base_url="http://localhost:8000").sync() as client:
            print("\nConnected to Tic-Tac-Toe environment!")
            result = client.reset()
            obs = result.observation
            
            while not result.done:
                print_board(obs.board)
                print(f"Current Player: {obs.current_player}")
                
                try:
                    user_input = input("Enter position (0-8) or 'q' to quit: ")
                    if user_input.lower() == 'q':
                        break
                    
                    pos = int(user_input)
                    if pos < 0 or pos > 8:
                        print("Invalid position. Must be between 0 and 8.")
                        continue
                except ValueError:
                    print("Please enter a valid integer.")
                    continue
                    
                result = client.step(TicTacToeAction(position=pos))
                obs = result.observation
                
                if obs.invalid_move:
                    print("\n[!] Invalid move! The cell is already taken or position is out of bounds. Try again.")
                else:
                    print(f"Action accepted. Reward: {result.reward}")
                    
            print_board(obs.board)
            if obs.is_tie:
                print("Game Over! It's a tie!")
            elif obs.winner:
                print(f"Game Over! Player {obs.winner} wins!")
            else:
                print("Game Terminated!")
                
    finally:
        print("\nShutting down server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main()
