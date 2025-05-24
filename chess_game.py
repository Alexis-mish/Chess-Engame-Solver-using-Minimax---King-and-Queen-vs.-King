import pygame
import sys

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 600, 600
SQUARE_SIZE = WIDTH // 8
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("King and Queen vs King")

# Colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
WHITE_PIECE_COLOR = (245, 245, 220)
BLACK_PIECE_COLOR = (20, 20, 20)
SELECTED_SQUARE = (255, 255, 0)

PIECES = {
    'w_king': '♔',
    'w_queen': '♕',
    'b_king': '♚'
}

def init_board():
    board = [['' for _ in range(8)] for _ in range(8)]
    board[0][4] = 'w_king'
    board[0][5] = 'w_queen'
    board[7][0] = 'b_king'
    return board

def on_board(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def find_piece(board, piece):
    for r in range(8):
        for c in range(8):
            if board[r][c] == piece:
                return (r, c)
    return None

def get_king_moves(board, r, c, white):
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    moves = []
    enemy_prefix = 'b' if white else 'w'
    if white:
        bk = find_piece(board, 'b_king')
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if on_board(nr, nc):
            cell = board[nr][nc]
            if cell == '' or cell.startswith(enemy_prefix):
                if white and bk and abs(nr - bk[0]) <= 1 and abs(nc - bk[1]) <= 1:
                    continue
                moves.append((nr, nc))
    return moves

def get_queen_moves(board, r, c):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]
    moves = []
    bk = find_piece(board, 'b_king')
    wk = find_piece(board, 'w_king')
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while on_board(nr, nc):
            if board[nr][nc] == '':
                # Avoid queen moving behind white king relative to black king
                if wk and bk:
                    v_q_bk = (bk[0] - r, bk[1] - c)
                    v_q_mv = (nr - r, nc - c)
                    v_q_wk = (wk[0] - r, wk[1] - c)
                    dot1 = v_q_bk[0]*v_q_mv[0] + v_q_bk[1]*v_q_mv[1]
                    dot2 = v_q_bk[0]*v_q_wk[0] + v_q_bk[1]*v_q_wk[1]
                    if dot1 < 0 and dot2 > 0:
                        break
                moves.append((nr, nc))
            else:
                if board[nr][nc].startswith('b'):
                    moves.append((nr, nc))
                break
            nr += dr
            nc += dc
    return moves

def is_square_attacked_by_white(board, r, c):
    wk = find_piece(board, 'w_king')
    wq = find_piece(board, 'w_queen')
    if wk and (r, c) in get_king_moves(board, wk[0], wk[1], True):
        return True
    if wq and (r, c) in get_queen_moves(board, wq[0], wq[1]):
        return True
    return False

def is_in_check(board, bk_pos):
    if not bk_pos:
        return False
    return is_square_attacked_by_white(board, bk_pos[0], bk_pos[1])

def get_black_king_moves(board):
    pos = find_piece(board, 'b_king')
    if not pos:
        return []
    moves = []
    for mr, mc in get_king_moves(board, pos[0], pos[1], False):
        if not is_square_attacked_by_white(board, mr, mc):
            wk = find_piece(board, 'w_king')
            if wk and abs(mr - wk[0]) <= 1 and abs(mc - wk[1]) <= 1:
                continue
            moves.append((mr, mc))
    return moves

def no_legal_black_moves(board):
    return len(get_black_king_moves(board)) == 0

def is_checkmate(board):
    bk = find_piece(board, 'b_king')
    return bk is not None and is_in_check(board, bk) and no_legal_black_moves(board)

def is_stalemate(board):
    bk = find_piece(board, 'b_king')
    return bk is not None and (not is_in_check(board, bk)) and no_legal_black_moves(board)

def evaluate(board):
    if is_checkmate(board):
        return 1000
    if is_stalemate(board):
        return 0
    bk = find_piece(board, 'b_king')
    if not bk:
        return 1000
    black_moves = get_black_king_moves(board)
    score = -len(black_moves) * 10
    wq = find_piece(board, 'w_queen')
    wk = find_piece(board, 'w_king')
    if wq:
        dist_q = abs(wq[0] - bk[0]) + abs(wq[1] - bk[1])
        score += (14 - dist_q) * 10
    if wk:
        dist_k = abs(wk[0] - bk[0]) + abs(wk[1] - bk[1])
        score += (14 - dist_k) * 5
    if is_in_check(board, bk):
        score += 100
    return score

def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or is_checkmate(board) or is_stalemate(board):
        return evaluate(board)
    if maximizing:
        max_eval = float('-inf')
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.startswith('w'):
                    moves = get_king_moves(board, r, c, True) if piece == 'w_king' else get_queen_moves(board, r, c)
                    for mr, mc in moves:
                        newb = [row[:] for row in board]
                        newb[mr][mc] = piece
                        newb[r][c] = ''
                        val = minimax(newb, depth-1, alpha, beta, False)
                        if val > max_eval:
                            max_eval = val
                        alpha = max(alpha, val)
                        if beta <= alpha:
                            break
        return max_eval
    else:
        bk_pos = find_piece(board, 'b_king')
        moves = get_black_king_moves(board)
        if not moves:
            return 1000 if is_in_check(board, bk_pos) else 0
        min_eval = float('inf')
        for mr, mc in moves:
            newb = [row[:] for row in board]
            newb[mr][mc] = 'b_king'
            oldr, oldc = bk_pos
            newb[oldr][oldc] = ''
            val = minimax(newb, depth-1, alpha, beta, True)
            min_eval = min(min_eval, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_eval

def computer_move(board):
    best_val = float('-inf')
    best_move = None
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.startswith('w'):
                moves = get_king_moves(board, r, c, True) if piece == 'w_king' else get_queen_moves(board, r, c)
                for mr, mc in moves:
                    newb = [row[:] for row in board]
                    newb[mr][mc] = piece
                    newb[r][c] = ''
                    val = minimax(newb, 3, float('-inf'), float('inf'), False)
                    if val > best_val:
                        best_val = val
                        best_move = (r, c, mr, mc)
    if best_move:
        r, c, mr, mc = best_move
        board[mr][mc] = board[r][c]
        board[r][c] = ''
        print(f"Computer moves {board[mr][mc]} from ({r},{c}) to ({mr},{mc})")
        return True
    return False

def draw_board(win, selected=None):
    for r in range(8):
        for c in range(8):
            color = LIGHT_SQUARE if (r+c) % 2 == 0 else DARK_SQUARE
            if selected == (r,c):
                color = SELECTED_SQUARE
            pygame.draw.rect(win, color, (c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(win, board):
    font = pygame.font.SysFont("segoeuisymbol", 72)
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p:
                color = WHITE_PIECE_COLOR if p.startswith('w') else BLACK_PIECE_COLOR
                text = font.render(PIECES[p], True, color)
                rect = text.get_rect(center=(c*SQUARE_SIZE + SQUARE_SIZE//2, r*SQUARE_SIZE + SQUARE_SIZE//2))
                win.blit(text, rect)

def main():
    board = init_board()
    turn = 'player'
    selected = None
    game_over = False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == 'player' and not game_over:
                mx, my = pygame.mouse.get_pos()
                c, r = mx // SQUARE_SIZE, my // SQUARE_SIZE
                if selected is None:
                    if board[r][c] == 'b_king':
                        selected = (r, c)
                else:
                    sr, sc = selected
                    moves = get_black_king_moves(board)
                    if (r, c) in moves:
                        board[r][c] = 'b_king'
                        board[sr][sc] = ''
                        turn = 'computer'
                    selected = None

        if not game_over and turn == 'computer':
            moved = computer_move(board)
            if moved:
                turn = 'player'

        bk = find_piece(board, 'b_king')
        if is_checkmate(board):
            print("Checkmate! Computer wins!")
            game_over = True
        elif is_stalemate(board):
            print("Stalemate! Draw!")
            game_over = True
        elif bk is None:
            print("Black king captured! Computer wins!")
            game_over = True

        draw_board(WINDOW, selected)
        draw_pieces(WINDOW, board)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()

