import time
from board import GameEngine, Move
from config import *

# ==============================================================================
# TODO: Import your AI agent class here.
# Ensure your file is named [TEAM NAME].py and class is [TEAM NAME] (uppercase).
# Example: from TEAM_EXCALIBUR import TEAM_EXCALIBUR
# ==============================================================================

from SOLO import SOLO 


PIECE_SYMBOLS = {
    'wP': '♟', 'bP': '♙',
    'wN': '♞', 'bN': '♘',
    'wB': '♝', 'bB': '♗',
    'wK': '♚', 'bK': '♔',
    EMPTY_SQUARE: ' '
}


class PlayerClock:
    def __init__(self, white_time, black_time):
        self.white_time = white_time
        self.black_time = black_time

    def get_time_str(self, t):
        m = int(t // 60)
        s = int(max(0, t % 60))
        return f"{m:02d}:{s:02d}"


def display_board(engine, clock, white_player, black_player):
    print("\n     a   b   c   d")
    print("   ┌───┬───┬───┬───┐")

    for r in range(BOARD_HEIGHT):
        rank = 8 - r
        row = f" {rank} │"

        for c in range(BOARD_WIDTH):
            piece = engine.board[r][c]
            row += f" {PIECE_SYMBOLS.get(piece, ' ')} │"

        row += f" {rank}"

        if r == 2:
            row += f"   Black ({black_player.__class__.__name__}): {clock.get_time_str(clock.black_time)}"
        if r == 5:
            row += f"   White ({white_player.__class__.__name__}): {clock.get_time_str(clock.white_time)}"

        print(row)
        if r < BOARD_HEIGHT - 1:
            print("   ├───┼───┼───┼───┤")

    print("   └───┴───┴───┴───┘")
    print("     a   b   c   d")


def run_game(white_player_type, black_player_type, total_time_seconds=60):
    white_points = 0
    black_points = 0

    engine = GameEngine()
    white_player = white_player_type(engine)
    black_player = black_player_type(engine)

    clock = PlayerClock(total_time_seconds, total_time_seconds)
    turn_counter = 0

    print("-" * 50)
    print(f"Match: {white_player.__class__.__name__} vs {black_player.__class__.__name__}")
    print("-" * 50)

    display_board(engine, clock, white_player, black_player)

    winner = None
    reason = ""

    while turn_counter < 150:
        if engine.get_game_state() != "ongoing":
            break

        player = white_player if engine.white_to_move else black_player
        color = "White" if engine.white_to_move else "Black"

        start = time.time()
        try:
            move = player.get_best_move()
        except Exception as e:
            print(f"{color} ERROR:", e)
            move = None

        elapsed = time.time() - start

        if engine.white_to_move:
            clock.white_time -= elapsed
            if clock.white_time <= 0:
                winner, reason = "Black", "Time Limit Exceeded"
                break
        else:
            clock.black_time -= elapsed
            if clock.black_time <= 0:
                winner, reason = "White", "Time Limit Exceeded"
                break

        if move is None:
            winner = "Black" if engine.white_to_move else "White"
            reason = "No Move Returned"
            break

        if move.piece_captured != EMPTY_SQUARE:
            pts = abs(PIECE_VALUES.get(move.piece_captured, 0))
            if engine.white_to_move:
                white_points += pts
            else:
                black_points += pts

        engine.make_move(move)

        if engine.is_in_check():
            if not engine.white_to_move:
                white_points += 2
            else:
                black_points += 2

        display_board(engine, clock, white_player, black_player)
        turn_counter += 1

    print("\n=============== GAME OVER ===============")
    final_state = engine.get_game_state()

    if winner or final_state == "checkmate":
        if not winner:
            winner = "Black" if engine.white_to_move else "White"
            reason = "Checkmate"

        print(f"Winner: {winner} ({reason})")

        if winner == "White":
            white_points = 600 if reason == "Checkmate" else white_points
            black_points = 0
        else:
            black_points = 600 if reason == "Checkmate" else black_points
            white_points = 0
    else:
        print("Draw / Stalemate")

    print(f"\nFinal Score → White: {white_points} | Black: {black_points}")


if __name__ == "__main__":
    run_game(
        white_player_type=SOLO,
        black_player_type=SOLO
    )
