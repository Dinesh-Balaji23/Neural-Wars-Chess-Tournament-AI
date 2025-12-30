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
        self._tt = {}
        self._current_pv = []

    def get_best_move(self):
        legal_moves = self.board.get_legal_moves()
        if not legal_moves:
            return None

        maximizing = self.board.white_to_move
        ordered_moves = self._order_moves(legal_moves)
        best_move = ordered_moves[0]
        best_score = float('-inf') if maximizing else float('inf')

        self._time_budget = self._allocate_time(len(legal_moves))
        self._search_start = time.time()
        self._time_exceeded = False

        for depth in range(self.min_depth, self.max_depth + 1):
            alpha, beta = float('-inf'), float('inf')
            current_best = None
            current_score = float('-inf') if maximizing else float('inf')
            current_line = []

            for index, move in enumerate(ordered_moves):
                self.board.make_move(move)
                gives_check = self.board.is_in_check()
                extension = self._extension_for(move, gives_check)
                reduction = self._late_move_reduction(depth, index, move, gives_check)
                next_depth = max(0, depth - 1 + extension - reduction)
                score, child_line = self._alpha_beta(next_depth, alpha, beta)
                self.board.undo_move()

                if maximizing and score > current_score:
                    current_score = score
                    current_best = move
                    current_line = child_line
                elif not maximizing and score < current_score:
                    current_score = score
                    current_best = move
                    current_line = child_line

                if maximizing:
                    alpha = max(alpha, current_score)
                else:
                    beta = min(beta, current_score)

                if beta <= alpha or self._time_exceeded:
                    break

            if current_best:
                best_move = current_best
                best_score = current_score
                ordered_moves = self._promote_root_move(ordered_moves, best_move)
                self._record_history(best_move, depth)
                self._current_pv = [best_move] + current_line

            if self._time_exceeded:
                break

        elapsed = time.time() - self._search_start
        self._avg_move_time = 0.7 * self._avg_move_time + 0.3 * elapsed
        return best_move

    def evaluate_board(self):
        material = 0
        positional = 0
        board_state = self.board.board
        white_king = None
        black_king = None
        white_pawns = []
        black_pawns = []
        white_bishops = []
        black_bishops = []

        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                piece = board_state[r][c]
                if piece == EMPTY_SQUARE:
                    continue
                material += PIECE_VALUES.get(piece, 0)
                positional += self._pst_bonus(piece, r, c)

                if piece == WHITE_KING:
                    white_king = (r, c)
                elif piece == BLACK_KING:
                    black_king = (r, c)
                elif piece == WHITE_PAWN:
                    white_pawns.append((r, c))
                elif piece == BLACK_PAWN:
                    black_pawns.append((r, c))
                elif piece == WHITE_BISHOP:
                    white_bishops.append((r, c))
                elif piece == BLACK_BISHOP:
                    black_bishops.append((r, c))

        tempo = 3 if self.board.white_to_move else -3
        rep_count = self.board.get_repetition_count()
        repetition_penalty = 0
        if rep_count >= 2:
            penalty = 7 * rep_count
            repetition_penalty = -penalty if self.board.white_to_move else penalty

        king_safety = self._king_safety(white_king, black_king)
        pawn_structure = self._pawn_structure_score(white_pawns, black_pawns)
        bishop_activity = self._bishop_activity_score(white_bishops, black_bishops)
        mobility = self._mobility_score()

        return (material + positional + tempo + repetition_penalty +
                king_safety + pawn_structure + bishop_activity + mobility)

    def _alpha_beta(self, depth, alpha, beta):
        if time.time() - self._search_start >= self._time_budget:
            self._time_exceeded = True
            return self.evaluate_board(), []

        key = (self._hash_position(), depth)
        tt_entry = self._tt.get(key)
        if tt_entry and tt_entry[0] >= depth:
            return tt_entry[1], []

        legal_moves = self.board.get_legal_moves()
        if not legal_moves:
            value = self._evaluate_leaf(depth, legal_moves)
            self._store_tt(key, depth, value)
            return value, []

        if depth <= 0:
            value = self._quiescence(alpha, beta, self.board.white_to_move)
            self._store_tt(key, depth, value)
            return value, []

        maximizing = self.board.white_to_move
        if maximizing:
            value = float('-inf')
            best_line = []
            for index, move in enumerate(self._order_moves(legal_moves)):
                self.board.make_move(move)
                gives_check = self.board.is_in_check()
                extension = self._extension_for(move, gives_check)
                reduction = self._late_move_reduction(depth, index, move, gives_check)
                next_depth = max(0, depth - 1 + extension - reduction)
                score, child_line = self._alpha_beta(next_depth, alpha, beta)
                self.board.undo_move()
                value = max(value, score)
                if score == value:
                    best_line = [move] + child_line
                alpha = max(alpha, value)
                if beta <= alpha or self._time_exceeded:
                    break
            self._store_tt(key, depth, value)
            return value, best_line

        value = float('inf')
        best_line = []
        for index, move in enumerate(self._order_moves(legal_moves)):
            self.board.make_move(move)
            gives_check = self.board.is_in_check()
            extension = self._extension_for(move, gives_check)
            reduction = self._late_move_reduction(depth, index, move, gives_check)
            next_depth = max(0, depth - 1 + extension - reduction)
            score, child_line = self._alpha_beta(next_depth, alpha, beta)
            self.board.undo_move()
            value = min(value, score)
            if score == value:
                best_line = [move] + child_line
            beta = min(beta, value)
            if beta <= alpha or self._time_exceeded:
                break

        self._store_tt(key, depth, value)
        return value, best_line

    def _evaluate_leaf(self, depth, legal_moves):
        if not legal_moves:
            if self.board.is_in_check():
                mate_score = self._mate_value + depth
                return -mate_score if self.board.white_to_move else mate_score
            return 0
        return self.evaluate_board()

    def _quiescence(self, alpha, beta, maximizing):
        if time.time() - self._search_start >= self._time_budget:
            self._time_exceeded = True
            return self.evaluate_board()

        stand_pat = self.evaluate_board()
        if maximizing:
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if stand_pat < beta:
                beta = stand_pat

        capture_moves = [m for m in self.board.get_legal_moves() if m.piece_captured != EMPTY_SQUARE]
        for move in self._order_moves(capture_moves):
            self.board.make_move(move)
            score = self._quiescence(alpha, beta, not maximizing)
            self.board.undo_move()

            if maximizing:
                if score > alpha:
                    alpha = score
                if alpha >= beta or self._time_exceeded:
                    break
            else:
                if score < beta:
                    beta = score
                if beta <= alpha or self._time_exceeded:
                    break

        return alpha if maximizing else beta

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

    def _hash_position(self):
        board_tuple = tuple(tuple(row) for row in self.board.board)
        return (board_tuple, self.board.white_to_move)

    def _store_tt(self, key, depth, value):
        if self._time_exceeded:
            return
        self._tt[key] = (depth, value)
        if len(self._tt) > 5000:
            # Simple aging strategy to keep memory bounded
            for _ in range(1000):
                self._tt.pop(next(iter(self._tt)), None)

    @staticmethod
    def _promote_root_move(moves, best_move):
        reordered = [best_move]
        reordered.extend(m for m in moves if m is not best_move)
        return reordered

    def _king_safety(self, white_king, black_king):
        return self._king_safety_single(white_king, 'w') - self._king_safety_single(black_king, 'b')

    def _king_safety_single(self, king_pos, color):
        if king_pos is None:
            return 0
        row, col = king_pos
        home_row = BOARD_HEIGHT - 1 if color == 'w' else 0
        home_distance = abs(row - home_row)
        center = (BOARD_WIDTH - 1) / 2
        center_distance = abs(col - center)

        penalty = home_distance * 4 + center_distance * 3

        if self.board._is_square_attacked(king_pos, color):
            penalty += 15
        if self.board._is_attacked_by_pawn(king_pos, color):
            penalty += 12
        if self.board._is_attacked_by_knight(king_pos, color):
            penalty += 10
        if self.board._is_attacked_by_bishop(king_pos, color):
            penalty += 8
        if self.board._is_attacked_by_king(king_pos, color):
            penalty += 20

        return -penalty

    def _pawn_structure_score(self, white_pawns, black_pawns):
        white_score = self._pawn_structure_single(white_pawns, 'w')
        black_score = self._pawn_structure_single(black_pawns, 'b')
        return white_score - black_score

    def _pawn_structure_single(self, pawns, color):
        if not pawns:
            return 0
        score = 0
        for row, col in pawns:
            if self._is_passed_pawn(row, col, color):
                score += 14
            if self._is_isolated_pawn(col, color):
                score -= 10
        return score

    def _is_passed_pawn(self, row, col, color):
        opponent_pawn = BLACK_PAWN if color == 'w' else WHITE_PAWN
        direction = -1 if color == 'w' else 1
        r = row + direction
        while 0 <= r < BOARD_HEIGHT:
            for dc in (-1, 0, 1):
                c = col + dc
                if 0 <= c < BOARD_WIDTH and self.board.board[r][c] == opponent_pawn:
                    return False
            r += direction
        return True

    def _is_isolated_pawn(self, col, color):
        friendly_pawn = WHITE_PAWN if color == 'w' else BLACK_PAWN
        for c in (col - 1, col + 1):
            if not (0 <= c < BOARD_WIDTH):
                continue
            for r in range(BOARD_HEIGHT):
                if self.board.board[r][c] == friendly_pawn:
                    return False
        return True

    def _bishop_activity_score(self, white_bishops, black_bishops):
        white_score = self._bishop_block_penalty(white_bishops, 'w')
        black_score = self._bishop_block_penalty(black_bishops, 'b')
        return white_score - black_score

    def _bishop_block_penalty(self, bishops, color):
        if not bishops:
            return 0
        friendly_pawn = WHITE_PAWN if color == 'w' else BLACK_PAWN
        penalty = 0
        for r, c in bishops:
            for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                nr, nc = r + dr, c + dc
                if self.board._is_valid(nr, nc) and self.board.board[nr][nc] == friendly_pawn:
                    penalty -= 6
                    break
        return penalty

    def _mobility_score(self):
        white_moves = self._count_moves_for(True)
        black_moves = self._count_moves_for(False)
        threat_score = self._threat_score()
        return (white_moves - black_moves) * 0.8 + threat_score

    def _count_moves_for(self, white_to_move):
        original_turn = self.board.white_to_move
        self.board.white_to_move = white_to_move
        moves = len(self.board.get_legal_moves())
        self.board.white_to_move = original_turn
        return moves

    def _extension_for(self, move, gives_check):
        extension = 0
        if move.piece_captured != EMPTY_SQUARE:
            extension += 1
        if gives_check:
            extension += 1
        return extension

    def _late_move_reduction(self, depth, move_index, move, gives_check):
        if depth < 3 or move_index < 3:
            return 0
        if move.piece_captured != EMPTY_SQUARE or gives_check:
            return 0
        return 1

    def _threat_score(self):
        white_threats = self._count_hanging_pieces('w')
        black_threats = self._count_hanging_pieces('b')
        return (black_threats - white_threats) * 6

    def _count_hanging_pieces(self, color):
        opponent = 'b' if color == 'w' else 'w'
        score = 0
        for r in range(BOARD_HEIGHT):
            for c in range(BOARD_WIDTH):
                piece = self.board.board[r][c]
                if piece == EMPTY_SQUARE or piece[0] != color:
                    continue
                sq = (r, c)
                attacked = self._is_square_attacked_by(sq, opponent)
                defended = self._is_square_attacked_by(sq, color)
                if attacked and not defended:
                    score += abs(PIECE_VALUES.get(piece, 0)) // 10 + 1
        return score

    def _is_square_attacked_by(self, square, attacker_color):
        r, c = square
        board_state = self.board.board
        # Pawn attacks
        if attacker_color == 'w':
            pawn = WHITE_PAWN
            directions = [(1, -1), (1, 1)]
        else:
            pawn = BLACK_PAWN
            directions = [(-1, -1), (-1, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if self.board._is_valid(nr, nc) and board_state[nr][nc] == pawn:
                return True

        # Knight attacks
        knight = WHITE_KNIGHT if attacker_color == 'w' else BLACK_KNIGHT
        for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            nr, nc = r + dr, c + dc
            if self.board._is_valid(nr, nc) and board_state[nr][nc] == knight:
                return True

        # Bishop attacks
        bishop = WHITE_BISHOP if attacker_color == 'w' else BLACK_BISHOP
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr, nc = r + dr, c + dc
            while self.board._is_valid(nr, nc):
                piece = board_state[nr][nc]
                if piece != EMPTY_SQUARE:
                    if piece == bishop:
                        return True
                    break
                nr += dr
                nc += dc

        # King attacks
        king = WHITE_KING if attacker_color == 'w' else BLACK_KING
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr, nc = r + dr, c + dc
            if self.board._is_valid(nr, nc) and board_state[nr][nc] == king:
                return True

        return False