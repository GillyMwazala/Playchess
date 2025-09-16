import streamlit as st
import chess
import chess.svg
import base64
from chess_engine import ChessGame

def render_svg(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode()
    html = f'<img src="data:image/svg+xml;base64,{b64}" style="width: 400px; border:2px solid #444; border-radius:10px;"/>'
    st.markdown(html, unsafe_allow_html=True)

def square_name(row, col):
    files = 'abcdefgh'
    ranks = '87654321'
    return files[col] + ranks[row]

st.set_page_config(page_title="Interactive Chess App", layout="centered")
st.title("♟️ Interactive Chess App")
with st.expander("How to Play", expanded=False):
    st.markdown("Click a piece, then its destination square to make a move. Play vs human or AI. Each move shows a brief explanation.")

if "game" not in st.session_state:
    st.session_state.game = ChessGame()
if "history" not in st.session_state:
    st.session_state.history = []
if "move_explanation" not in st.session_state:
    st.session_state.move_explanation = ""
if "selected_square" not in st.session_state:
    st.session_state.selected_square = None

game = st.session_state.game

col1, col2 = st.columns([2, 1])

with col1:
    # Highlight last move if available
    lastmove = chess.Move.from_uci(st.session_state.history[-1]) if st.session_state.history else None
    svg_board = chess.svg.board(game.board, size=400, lastmove=lastmove)
    render_svg(svg_board)

    # Clickable squares (hidden, but used for selection logic)
    for row in range(8):
        cols = st.columns(8)
        for col in range(8):
            sq = square_name(row, col)
            btn_key = f"{row}_{col}_{st.session_state.selected_square}"
            if cols[col].button(" ", key=btn_key, help=sq, use_container_width=True):
                if st.session_state.selected_square is None:
                    # First click: select piece if it's the right color
                    piece = game.board.piece_at(chess.parse_square(sq))
                    if piece and ((piece.color and game.board.turn) or (not piece.color and not game.board.turn)):
                        st.session_state.selected_square = sq
                else:
                    # Second click: attempt move
                    move_uci = st.session_state.selected_square + sq
                    legal_moves = [m for m in game.get_legal_moves()]
                    # Try normal move
                    if move_uci in legal_moves:
                        success, explanation = game.push_move(move_uci)
                        if success:
                            st.session_state.history.append(move_uci)
                            st.session_state.move_explanation = explanation
                    # Try promotion to queen
                    elif move_uci + 'q' in legal_moves:
                        success, explanation = game.push_move(move_uci + 'q')
                        if success:
                            st.session_state.history.append(move_uci + 'q')
                            st.session_state.move_explanation = explanation
                    else:
                        st.warning("Illegal move.")
                    st.session_state.selected_square = None

    if game.is_game_over():
        st.markdown(f"### Game Over: {game.get_result()}")

with col2:
    mode = st.radio("Mode", ["Human vs Human", "Human vs AI"])
    if mode == "Human vs AI" and not game.is_game_over() and len(game.get_legal_moves()) > 0:
        if st.button("AI Move"):
            move, explanation = game.ai_move(level='random')
            st.session_state.history.append(move)
            st.session_state.move_explanation = explanation
    if st.button("Restart Game"):
        st.session_state.game = ChessGame()
        st.session_state.history = []
        st.session_state.move_explanation = ""
        st.session_state.selected_square = None

    st.write("#### Last Move Explanation:")
    st.info(st.session_state.move_explanation)

# Sidebar move list, formatted
st.sidebar.markdown("## Move History")
if st.session_state.history:
    move_list = ""
    for i in range(0, len(st.session_state.history), 2):
        move_no = i // 2 + 1
        white = st.session_state.history[i]
        black = st.session_state.history[i+1] if i+1 < len(st.session_state.history) else ""
        move_list += f"{move_no}. {white} {black}\n"
    st.sidebar.text_area("PGN", move_list, height=200)
else:
    st.sidebar.write("No moves yet.")
