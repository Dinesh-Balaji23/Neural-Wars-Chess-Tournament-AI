# Team Member : Dineshbalaji A
# Team Name : SOLO (I THINK)

# Disclaimer: No reinforcement learning methods were used in this solution.
from ai_player import AIPlayer
from config import *


class SOLO(AIPlayer):
    def __init__(self, board):
        super().__init__(board)
        self.depth = 4
        self._mate_value = 100000

    def get_best_move(self):
        legal_moves = self.board.get_legal_moves()
        if not legal_moves:
            return None

        best_move = legal_moves[0]
        maximizing = self.board.white_to_move
        best_score = float('-inf') if maximizing else float('inf')
        alpha, beta = float('-inf'), float('inf')

        for move in self._order_moves(legal_moves):
            self.board.make_move(move)
            score = self._alpha_beta(self.depth - 1, alpha, beta)
            self.board.undo_move()

            if maximizing and score > best_score:
                best_score = score
                best_move = move
            elif not maximizing and score < best_score:
                best_score = score
                best_move = move

            if maximizing:
                alpha = max(alpha, best_score)
            else:
                beta = min(beta, best_score)

            if beta <= alpha:
                break

        return best_move

    def evaluate_board(self):
        material = 0
        positional = 0
        board_state = self.board.board

        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                piece = board_state[r][c]
                if piece == EMPTY_SQUARE:
                    continue
                material += PIECE_VALUES.get(piece, 0)
                positional += self._pst_bonus(piece, r, c)

        tempo = 3 if self.board.white_to_move else -3
        repetition_penalty = -5 if self.board.get_repetition_count() >= 2 else 0

        return material + positional + tempo + repetition_penalty

    def _alpha_beta(self, depth, alpha, beta):
        legal_moves = self.board.get_legal_moves()
        if depth == 0 or not legal_moves:
            return self._evaluate_leaf(depth, legal_moves)

        maximizing = self.board.white_to_move
        if maximizing:
            value = float('-inf')
            for move in self._order_moves(legal_moves):
                self.board.make_move(move)
                score = self._alpha_beta(depth - 1, alpha, beta)
                self.board.undo_move()
                value = max(value, score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value

        value = float('inf')
        for move in self._order_moves(legal_moves):
            self.board.make_move(move)
            score = self._alpha_beta(depth - 1, alpha, beta)
            self.board.undo_move()
            value = min(value, score)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

    def _evaluate_leaf(self, depth, legal_moves):
        if not legal_moves:
            if self.board.is_in_check():
                mate_score = self._mate_value + depth
                return -mate_score if self.board.white_to_move else mate_score
            return 0
        return self.evaluate_board()

    def _pst_bonus(self, piece, row, col):
        if piece == WHITE_PAWN:
            return PAWN_PST[row][col]
        if piece == BLACK_PAWN:
            return -PAWN_PST[BOARD_HEIGHT - 1 - row][col]
        if piece == WHITE_KNIGHT:
            return KNIGHT_PST[row][col]
        if piece == BLACK_KNIGHT:
            return -KNIGHT_PST[BOARD_HEIGHT - 1 - row][col]
        if piece == WHITE_BISHOP:
            return BISHOP_PST[row][col]
        if piece == BLACK_BISHOP:
            return -BISHOP_PST[BOARD_HEIGHT - 1 - row][col]
        if piece == WHITE_KING:
            return KING_PST_LATE_GAME[row][col]
        if piece == BLACK_KING:
            return -KING_PST_LATE_GAME[BOARD_HEIGHT - 1 - row][col]
        return 0

    def _order_moves(self, moves):
        return sorted(moves, key=self._move_priority, reverse=True)

    def _move_priority(self, move):
        capture_value = abs(PIECE_VALUES.get(move.piece_captured, 0))
        mover_value = abs(PIECE_VALUES.get(move.piece_moved, 0))
        return capture_value * 100 - mover_value