import streamlit as st
import chess
from streamlit_chessboard import chessboard
import requests
from chess_engine import ChessGame

def lichess_best_move(fen):
    """Query the Lichess Cloud Evaluation API for the best move in the given FEN position."""
    api_key = st.secrets["lichess_api_key"]
    url = "https://lichess.org/api/cloud-eval"
    params = {"fen": fen, "multiPv": 1}
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data["pvs"][0]["moves"].split()[0], data["pvs"][0].get("cp", None)
    else:
        return None, None

st.set_page_config(page_title="Interactive Chess App", layout="centered")
st.title("♟️ Streamlit Chess App (Drag or Click Pieces!)")

with st.expander("How to Play", expanded=False):
    st.markdown(
        "Move pieces by dragging or clicking them on the board. "
        "You can also get the best move suggestion from Lichess Cloud Stockfish engine by clicking the button."
    )

if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "history" not in st.session_state:
    st.session_state.history = []
if "move_explanation" not in st.session_state:
    st.session_state.move_explanation = ""

board = st.session_state.board

col1, col2 = st.columns([2, 1])

with col1:
    fen, move = chessboard(
        fen=board.fen(),
        key="chessboard",
        width=400,
        piece_style="alpha"  # You can also try "merida", "uscf", "wikipedia"
    )

    # If user makes a move on the board, apply it
    if move:
        move_uci = move['from'] + move['to']
        # Try promotion (always promote to queen for simplicity)
        if chess.Move.from_uci(move_uci) not in board.legal_moves:
            move_uci += "q"
        try:
            board.push_uci(move_uci)
            st.session_state.history.append(move_uci)
            st.session_state.move_explanation = f"Move played: {move_uci}"
        except Exception as e:
            st.warning("Illegal move!")

    st.write("#### Last Move Explanation:")
    st.info(st.session_state.move_explanation)

    if board.is_game_over():
        st.markdown(f"### Game Over: {board.result()}")

    fen = board.fen()
    if st.button("Get Best Move (Lichess AI)"):
        with st.spinner("Querying Lichess Cloud Engine..."):
            best_move, eval_cp = lichess_best_move(fen)
        if best_move:
            eval_text = f"Evaluation: {'+' if eval_cp and eval_cp >= 0 else ''}{eval_cp} cp" if eval_cp is not None else ""
            st.success(f"Lichess Cloud recommends: **{best_move}** {eval_text}")
        else:
            st.error("Could not retrieve cloud analysis.")

    if st.button("Restart Game"):
        st.session_state.board = chess.Board()
        st.session_state.history = []
        st.session_state.move_explanation = ""

with col2:
    st.markdown("## Move History")
    if st.session_state.history:
        move_list = ""
        for i in range(0, len(st.session_state.history), 2):
            move_no = i // 2 + 1
            white = st.session_state.history[i]
            black = st.session_state.history[i+1] if i+1 < len(st.session_state.history) else ""
            move_list += f"{move_no}. {white} {black}\n"
        st.text_area("PGN", move_list, height=200)
    else:
        st.write("No moves yet.")

    # Optionally, add a mode selector and AI move button if you want
