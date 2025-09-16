import streamlit as st
from streamlit_chessboard import st_chessboard
import chess
from chess_engine import ChessGame

st.set_page_config(page_title="Interactive Chess App", layout="centered")
st.title("♟️ Interactive Chess App")
st.markdown(
    "Play chess against another human or an AI. Click pieces to move! Each move gets a brief explanation."
)

if "game" not in st.session_state:
    st.session_state.game = ChessGame()
if "history" not in st.session_state:
    st.session_state.history = []
if "move_explanation" not in st.session_state:
    st.session_state.move_explanation = ""

game = st.session_state.game

col1, col2 = st.columns([2, 1])

with col1:
    # Use ChessBoard component
    fen = game.get_board_fen()
    # Allow moves only if the game isn't over
    board_disabled = game.is_game_over()
    move = st_chessboard(
        fen=fen,
        key="chessboard",
        allow_move=not board_disabled,
        board_color="#f0d9b5",
        piece_style="merida",
        dark_square_color="#b58863",
        light_square_color="#f0d9b5"
    )
    if move:
        success, explanation = game.push_move(move["move"])
        if success:
            st.session_state.history.append(move["move"])
            st.session_state.move_explanation = explanation
        else:
            st.warning("Illegal move.")

    if game.is_game_over():
        st.markdown(f"### Game Over: {game.get_result()}")

with col2:
    mode = st.radio("Mode", ["Human vs Human", "Human vs AI"])
    if mode == "Human vs AI" and not game.is_game_over():
        if st.button("AI Move"):
            move, explanation = game.ai_move(level='random')
            st.session_state.history.append(move)
            st.session_state.move_explanation = explanation

    st.write("#### Last Move Explanation:")
    st.info(st.session_state.move_explanation)

    if st.button("Restart Game"):
        st.session_state.game = ChessGame()
        st.session_state.history = []
        st.session_state.move_explanation = ""

st.sidebar.markdown("## Move History")
st.sidebar.write(st.session_state.history)
