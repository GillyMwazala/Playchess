import streamlit as st
import chess
import chess.svg
from PIL import Image
import base64
import io
from chess_engine import ChessGame

def render_svg(svg_html):
    # Convert SVG to PNG for Streamlit display
    import cairosvg
    png_data = cairosvg.svg2png(bytestring=svg_html.encode('utf-8'))
    return Image.open(io.BytesIO(png_data))

def square_name(row, col):
    files = 'abcdefgh'
    ranks = '87654321'
    return files[col] + ranks[row]

st.set_page_config(page_title="Interactive Chess App", layout="centered")
st.title("♟️ Interactive Chess App (Clickable Board)")
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
    svg_board = chess.svg.board(game.board, size=400,
                                lastmove=chess.Move.from_uci(st.session_state.history[-1]) if st.session_state.history else None,
                                squares=[])
    board_img = render_svg(svg_board)
    st.image(board_img)

    # Render clickable squares using Streamlit buttons in an 8x8 grid
    st.write("Click on a square to select a piece or move.")
    grid_cols = st.columns(8)
    for row in range(8):
        cols = st.columns(8)
        for col in range(8):
            sq = square_name(row, col)
            btn_key = f"{row}_{col}_{st.session_state.selected_square}"
            label = " "  # No text, just a blank button
            if cols[col].button(label, key=btn_key, help=sq, use_container_width=True):
                if st.session_state.selected_square is None:
                    # First click: select piece if it's the right color
                    piece = game.board.piece_at(chess.parse_square(sq))
                    if piece and ((piece.color and game.board.turn) or (not piece.color and not game.board.turn)):
                        st.session_state.selected_square = sq
                else:
                    # Second click: attempt move from selected_square to sq
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

st.sidebar.markdown("## Move History")
st.sidebar.write(st.session_state.history)
