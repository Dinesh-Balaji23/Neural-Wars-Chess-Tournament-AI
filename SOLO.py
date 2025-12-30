# Team Member : Dineshbalaji A
# Team Name : SOLO (I THINK)

# Disclaimer: No reinforcement learning methods were used in this solution.
from ai_player import AIPlayer
from config import *
import time


class SOLO(AIPlayer):
    def __init__(self, board):
        super().__init__(board)
        self.min_depth = 2
        self.max_depth = 5
        self.time_budget = 0.6
        self._avg_move_time = 0.0
        self._mate_value = 100000
        self._history_scores = {}

    def get_best_move(self):
        legal_moves = self.board.get_legal_moves()
        if not legal_moves:
            return None

        maximizing = self.board.white_to_move
        best_move = legal_moves[0]
        best_score = float('-inf') if maximizing else float('inf')

        self._time_budget = self._allocate_time(len(legal_moves))
        self._search_start = time.time()
        self._time_exceeded = False

        for depth in range(self.min_depth, self.max_depth + 1):
            alpha, beta = float('-inf'), float('inf')
            current_best = best_move
            current_score = best_score

            for move in self._order_moves(legal_moves):
                self.board.make_move(move)
                score = self._alpha_beta(depth - 1, alpha, beta)
                self.board.undo_move()

                if maximizing and score > current_score:
                    current_score = score
                    current_best = move
                elif not maximizing and score < current_score:
                    current_score = score
                    current_best = move

                if maximizing:
                    alpha = max(alpha, current_score)
                else:
                    beta = min(beta, current_score)

                if beta <= alpha or self._time_exceeded:
                    break

            best_move = current_best
            best_score = current_score
            self._record_history(best_move, depth)

            if self._time_exceeded:
                break

        elapsed = time.time() - self._search_start
        self._avg_move_time = 0.7 * self._avg_move_time + 0.3 * elapsed
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
        if time.time() - self._search_start >= self._time_budget:
            self._time_exceeded = True
            return self.evaluate_board()

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
        history = self._history_scores.get(self._move_key(move), 0)
        return capture_value * 100 + history - mover_value

    def _record_history(self, move, depth):
        if not move:
            return
        key = self._move_key(move)
        self._history_scores[key] = self._history_scores.get(key, 0) + depth * depth

    @staticmethod
    def _move_key(move):
        return (move.start_row, move.start_col, move.end_row, move.end_col)

    def _allocate_time(self, branching_factor):
        base = self.time_budget
        if branching_factor > 12:
            base *= 0.7
        elif branching_factor < 6:
            base *= 1.25
        if self._avg_move_time > 0.6:
            base *= 0.75
        elif self._avg_move_time < 0.3:
            base *= 1.15
        return max(0.2, min(0.9, base))