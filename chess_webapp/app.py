import streamlit as st
import chess
import chess.svg
import base64
from chess_engine import ChessGame

def get_square_color(row, col):
    return "#f0d9b5" if (row + col) % 2 == 0 else "#b58863"

def square_name(row, col):
    files = 'abcdefgh'
    ranks = '87654321'
    return files[col] + ranks[row]

def render_svg(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode()
    html = f'<img src="data:image/svg+xml;base64,{b64}" style="width: 400px; border:2px solid #444; border-radius:10px;"/>'
    st.markdown(html, unsafe_allow_html=True)

st.set_page_config(page_title="Interactive Chess App", layout="centered")
st.title("♟️ Interactive Chess App (Clickable Board)")

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
    st.write("### Chess Board")
    # Interactive 8x8 grid of buttons—NO double board, just this grid!
    board = game.board
    for row in range(8):
        cols = st.columns(8)
        for col in range(8):
            sq = square_name(row, col)
            piece = board.piece_at(chess.parse_square(sq))
            label = piece.unicode_symbol() if piece else " "
            btn_key = f"square_{sq}_{st.session_state.selected_square}"

            # Highlight selected square
            style = f"background-color: {'#fffa65' if sq == st.session_state.selected_square else get_square_color(row, col)}; height:45px; font-size:28px;"
            # Render each square as a button
            if cols[col].button(label, key=btn_key, help=sq, use_container_width=True):
                # If no square selected, select a piece
                if st.session_state.selected_square is None:
                    if piece and piece.color == board.turn:
                        st.session_state.selected_square = sq
                else:
                    # Try making a move from selected_square to this one
                    move_uci = st.session_state.selected_square + sq
                    legal_moves = [m.uci() for m in board.legal_moves]
                    if move_uci in legal_moves:
                        success, explanation = game.push_move(move_uci)
                        if success:
                            st.session_state.history.append(move_uci)
                            st.session_state.move_explanation = explanation
                    elif move_uci + "q" in legal_moves:  # for pawn promotion
                        success, explanation = game.push_move(move_uci + "q")
                        if success:
                            st.session_state.history.append(move_uci + "q")
                            st.session_state.move_explanation = explanation
                    else:
                        st.warning("Illegal move.")
                    st.session_state.selected_square = None  # Reset selection after move/attempt

    if game.is_game_over():
        st.markdown(f"### Game Over: {game.get_result()}")

with col2:
    mode = st.radio("Mode", ["Human vs Human", "Human vs AI"])
    if mode == "Human vs AI" and not game.is_game_over() and len(list(game.board.legal_moves)) > 0:
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
