import streamlit as st
import chess
import chess.svg
from chess_engine import ChessGame

def render_svg(svg):
    html = f'<img src="data:image/svg+xml;utf8,{svg}" style="width: 400px"/>'
    st.markdown(html, unsafe_allow_html=True)

st.set_page_config(page_title="Interactive Chess App", layout="centered")
st.title("♟️ Interactive Chess App")
st.markdown("Play chess against another human or an AI. After each move, you'll see a brief explanation of the move's strategy.")

if "game" not in st.session_state:
    st.session_state.game = ChessGame()
if "history" not in st.session_state:
    st.session_state.history = []
if "move_explanation" not in st.session_state:
    st.session_state.move_explanation = ""

game = st.session_state.game

col1, col2 = st.columns([2, 1])

with col1:
    board_svg = chess.svg.board(game.board, size=400)
    render_svg(board_svg)
    if game.is_game_over():
        st.markdown(f"### Game Over: {game.get_result()}")

with col2:
    mode = st.radio("Mode", ["Human vs Human", "Human vs AI"])
    st.write("Legal moves:", ", ".join(game.get_legal_moves()))
    move_input = st.text_input("Enter your move (UCI, e.g. e2e4):", key="move_input")
    if st.button("Make Move"):
        success, explanation = game.push_move(move_input.strip())
        if success:
            st.session_state.history.append(move_input.strip())
            st.session_state.move_explanation = explanation
            st.experimental_rerun()
        else:
            st.warning(explanation)
    if mode == "Human vs AI" and not game.is_game_over() and len(game.get_legal_moves()) > 0:
        if st.button("AI Move"):
            move, explanation = game.ai_move(level='random')
            st.session_state.history.append(move)
            st.session_state.move_explanation = explanation
            st.experimental_rerun()
    st.write("#### Last Move Explanation:")
    st.info(st.session_state.move_explanation)
    if st.button("Restart Game"):
        st.session_state.game = ChessGame()
        st.session_state.history = []
        st.session_state.move_explanation = ""
        st.experimental_rerun()

st.sidebar.markdown("## Move History")
st.sidebar.write(st.session_state.history)