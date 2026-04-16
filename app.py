import gradio as gr
from fastapi import FastAPI
from tic_tac_toe.server.app import app as openenv_app
from tic_tac_toe.server.tic_tac_toe_environment import TicTacToeEnvironment
from tic_tac_toe.models import TicTacToeAction

css = """
.board-container {
    max-width: 350px !important;
    margin: 0 auto !important;
    background: rgba(30, 41, 59, 0.8) !important;
    padding: 20px !important;
    border-radius: 16px !important;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
.board-row {
    display: flex !important;
    flex-wrap: nowrap !important;
    justify-content: center !important;
    gap: 10px !important;
    margin-bottom: 10px !important;
}
.cell-btn {
    height: 100px !important;
    width: 100px !important;
    min-width: 100px !important;
    max-width: 100px !important;
    flex-grow: 0 !important;
    flex-shrink: 0 !important;
    margin: 5px auto !important;
    font-size: 3rem !important;
    font-weight: 800 !important;
    color: #f8fafc !important;
    background: rgba(15, 23, 42, 0.6) !important;
    border: 2px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 12px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}
.cell-btn:hover {
    background: rgba(51, 65, 85, 0.8) !important;
    transform: translateY(-2px) scale(1.02) !important;
    border-color: rgba(148, 163, 184, 0.4) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
}
.reset-btn {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 10px 30px !important;
    font-weight: bold !important;
    font-size: 1.1rem !important;
    max-width: 250px !important;
    margin: 30px auto 10px auto !important;
    display: block !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.5) !important;
}
.reset-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 15px 25px -5px rgba(59, 130, 246, 0.6) !important;
}
.status-text {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
.status-text textarea {
    text-align: center !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #60a5fa !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
"""

def make_ui():
    with gr.Blocks(title="Tic-Tac-Toe", theme=gr.themes.Base(), css=css) as demo:
        gr.Markdown(
            "<h1 style='text-align: center; color: #f8fafc; font-size: 3rem; margin-bottom: 0.5rem;'>Tic-Tac-Toe</h1>"
            "<p style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem;'>Play against RL agents or locally via OpenEnv API!</p>"
        )
        
        state_env = gr.State(None)
        
        board_buttons = []
        with gr.Column(elem_classes="board-container"):
            for i in range(3):
                with gr.Row(elem_classes="board-row"):
                    for j in range(3):
                        btn = gr.Button(" ", scale=0, min_width=100, elem_classes="cell-btn", elem_id=f"btn_{i*3+j}")
                        board_buttons.append(btn)
        
        status = gr.Textbox(label="", value="Game Ready", elem_classes="status-text", show_label=False)
        reset_btn = gr.Button("Reset Game", elem_classes="reset-btn")
        
        def reset():
            env = TicTacToeEnvironment()
            obs = env.reset()
            updates = [env] + [gr.Button(value=b) for b in obs.board] + [f"Player {obs.current_player}'s turn | Reward: {obs.reward}"]
            return tuple(updates)
            
        def step(pos, env):
            if env is None:
                env = TicTacToeEnvironment()
                env.reset()
                
            obs = env.step(TicTacToeAction(position=pos))
            
            if obs.invalid_move:
                msg = f"[!] Invalid move! Cell already taken. | Reward: {obs.reward}"
            elif obs.winner:
                msg = f"🏆 Game Over! Player {obs.winner} wins! | Reward: {obs.reward}"
            elif obs.is_tie:
                msg = f"🤝 Game Over! It's a tie! | Reward: {obs.reward}"
            else:
                msg = f"Player {obs.current_player}'s turn | Reward: {obs.reward}"
                
            updates = [env] + [gr.Button(value=obs.board[i]) for i in range(9)] + [msg]
            return tuple(updates)
            
        for idx, btn in enumerate(board_buttons):
            # Using pos=idx in lambda to correctly bind the value inside the loop loop
            btn.click(
                fn=lambda e, pos=idx: step(pos, e),
                inputs=[state_env],
                outputs=[state_env] + board_buttons + [status]
            )
            
        reset_btn.click(
            fn=reset,
            outputs=[state_env] + board_buttons + [status]
        )
        
        demo.load(fn=reset, outputs=[state_env] + board_buttons + [status])
        
    return demo

demo = make_ui()

# Combine openenv API + gradio! 
# When deploying to huggingface, `uvicorn app:app` will run and host both interface and API.
app = gr.mount_gradio_app(openenv_app, demo, path="/")
