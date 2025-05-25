import pygame
import sys
import threading
import random # Para Zobrist Hashing

# --- Pygame Initialization (existing) ---
pygame.init()
WIDTH, HEIGHT = 600, 600
SQUARE_SIZE = WIDTH // 8
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("King and Queen vs King")

# Colors (existing)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
WHITE_PIECE_COLOR = (245, 245, 220)
BLACK_PIECE_COLOR = (20, 20, 20)
SELECTED_SQUARE = (255, 255, 0)
VALID_MOVE_COLOR = (0, 255, 0)
INVALID_MOVE_COLOR = (255, 0, 0)
FONT = pygame.font.SysFont("Arial", 32)

PIECES = {
    'w_king': '♔',
    'w_queen': '♕',
    'b_king': '♚'
}

# --- Global Transposition Table and Zobrist Keys ---
# Definimos los tipos de piezas y jugadores para Zobrist Hashing
Z_PIECES = ['w_king', 'w_queen', 'b_king']
Z_NUM_PIECES = len(Z_PIECES) # 3
Z_BOARD_SIZE = 8 * 8 # 64

# Generar claves Zobrist aleatorias
ZOBRIST_KEYS = [[[0 for _ in range(Z_NUM_PIECES)] for _ in range(Z_BOARD_SIZE)]] # Para piezas en casillas

# Inicializar las claves Zobrist una vez al inicio del programa
def init_zobrist_keys():
    # Usaremos un índice para mapear el nombre de la pieza a un número
    piece_to_index = {
        'w_king': 0,
        'w_queen': 1,
        'b_king': 2
    }
    global ZOBRIST_KEYS
    ZOBRIST_KEYS = [[[random.getrandbits(64) for _ in range(Z_NUM_PIECES)] for _ in range(Z_BOARD_SIZE)]]

    # También necesitamos una clave para el turno (aunque en tu juego es fijo, es buena práctica)
    # y para el enroque, etc. Pero aquí solo simplificaremos al estado del tablero.
    # Por simplicidad, en este juego solo hay 3 piezas, y el turno lo manejamos externamente,
    # así que el hash solo dependerá de la posición de las piezas.

# Llamar a la inicialización al inicio del script
init_zobrist_keys()

# Tabla de transposiciones global
# key: Zobrist hash
# value: {'score': int, 'depth': int, 'flag': str (EXACT, ALPHA, BETA)}
TRANSPOSITION_TABLE = {}

# Flags para el tipo de nodo
TT_EXACT = 0 # Valor exacto (alpha >= beta)
TT_ALPHA = 1 # Límite inferior (alpha se actualizó)
TT_BETA = 2  # Límite superior (beta se actualizó)

# --- Existing Game Logic Functions (copy paste from your code) ---
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
                  (0, -1),            (0, 1),
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

# --- Modified Evaluate Function ---
def evaluate(board):
    if is_checkmate(board):
        return 1000
    if is_stalemate(board):
        return 0

    bk = find_piece(board, 'b_king')
    if not bk:
        return 1000

    score = 0

    # 1. Movilidad del Rey Negro (Penaliza al rey negro por tener pocos movimientos)
    black_moves = get_black_king_moves(board)
    score += -len(black_moves) * 15

    # 2. Distancia del Rey Negro a la esquina más cercana (fuerza al rey negro a los bordes)
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    dist_to_corner = min(abs(bk[0]-cr)+abs(bk[1]-cc) for cr, cc in corners)
    score += (14 - dist_to_corner) * 5

    # 3. Proximidad de la Reina Blanca al Rey Negro (la reina acorrala al rey)
    wq = find_piece(board, 'w_queen')
    if wq:
        dist_q_bk = abs(wq[0] - bk[0]) + abs(wq[1] - bk[1])
        score += (14 - dist_q_bk) * 10

    # 4. Proximidad del Rey Blanco al Rey Negro (el rey blanco ayuda a acorralar)
    wk = find_piece(board, 'w_king')
    if wk:
        dist_wk_bk = abs(wk[0] - bk[0]) + abs(wk[1] - bk[1])
        score += (14 - dist_wk_bk) * 7

    # 5. Bonificación si el Rey Negro está en Jaque (siempre es bueno tenerlo en jaque)
    if is_in_check(board, bk):
        score += 100

    return score


# --- Zobrist Hashing Function ---
piece_to_zobrist_idx = {
    'w_king': 0,
    'w_queen': 1,
    'b_king': 2
}

def compute_zobrist_hash(board):
    h = 0
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece:
                piece_idx = piece_to_zobrist_idx[piece]
                square_idx = r * 8 + c
                h ^= ZOBRIST_KEYS[0][square_idx][piece_idx] # XOR con la clave aleatoria
    return h

# --- Modified Minimax with Transposition Table ---
def minimax(board, depth, alpha, beta, maximizing):
    # Calcula el hash de la posición actual
    current_hash = compute_zobrist_hash(board)

    # 1. Look up in Transposition Table
    if current_hash in TRANSPOSITION_TABLE:
        entry = TRANSPOSITION_TABLE[current_hash]
        if entry['depth'] >= depth: # Si la entrada tiene suficiente profundidad
            if entry['flag'] == TT_EXACT:
                return entry['score']
            elif entry['flag'] == TT_ALPHA and entry['score'] > alpha:
                alpha = entry['score']
            elif entry['flag'] == TT_BETA and entry['score'] < beta:
                beta = entry['score']
            if alpha >= beta: # Check for beta cutoff using stored value
                return entry['score']

    # Base case: depth 0 or game over
    if depth == 0 or is_checkmate(board) or is_stalemate(board):
        return evaluate(board)

    # Store original alpha/beta for flag checking
    original_alpha = alpha
    original_beta = beta
    best_score = float('-inf') if maximizing else float('inf')

    # Generate moves (consider move ordering here for more efficiency)
    moves_to_explore = []
    if maximizing: # White's turn (computer)
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.startswith('w'):
                    # Get moves and prioritize captures/checks for better alpha-beta pruning
                    current_piece_moves = get_king_moves(board, r, c, True) if piece == 'w_king' else get_queen_moves(board, r, c)
                    for mr, mc in current_piece_moves:
                        # Add a simple heuristic for move ordering: prioritize captures
                        # In this specific game, the only capture is of the black king
                        is_capture = (board[mr][mc] == 'b_king') # True if black king is on target square
                        moves_to_explore.append((is_capture, r, c, mr, mc, piece))
        # Sort moves: captures first, then other moves
        moves_to_explore.sort(key=lambda x: x[0], reverse=True)
    else: # Black's turn (player)
        bk_pos = find_piece(board, 'b_king')
        if bk_pos:
            current_piece_moves = get_black_king_moves(board)
            for mr, mc in current_piece_moves:
                moves_to_explore.append((0, bk_pos[0], bk_pos[1], mr, mc, 'b_king'))


    # Perform search
    for move_info in moves_to_explore:
        is_capture, r, c, mr, mc, piece = move_info

        newb = [row[:] for row in board]
        newb[mr][mc] = piece
        newb[r][c] = ''

        if maximizing:
            val = minimax(newb, depth - 1, alpha, beta, False)
            best_score = max(best_score, val)
            alpha = max(alpha, val)
        else:
            val = minimax(newb, depth - 1, alpha, beta, True)
            best_score = min(best_score, val)
            beta = min(beta, val)

        if beta <= alpha: # Alpha-beta cutoff
            break

    # 2. Store in Transposition Table
    entry_flag = TT_EXACT
    if best_score <= original_alpha: # Beta cutoff happened on the search
        entry_flag = TT_BETA
    elif best_score >= original_beta: # Alpha cutoff happened on the search
        entry_flag = TT_ALPHA

    TRANSPOSITION_TABLE[current_hash] = {
        'score': best_score,
        'depth': depth,
        'flag': entry_flag
    }

    return best_score

# --- Computer Move (unchanged logic, but uses the new minimax) ---
def computer_move(board):
    # Paso 1: Buscar mate en 1 (esto sigue siendo una optimización útil)
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.startswith('w'):
                moves = get_king_moves(board, r, c, True) if piece == 'w_king' else get_queen_moves(board, r, c)
                for mr, mc in moves:
                    newb = [row[:] for row in board]
                    newb[mr][mc] = piece
                    newb[r][c] = ''
                    if is_checkmate(newb):
                        board[mr][mc] = piece
                        board[r][c] = ''
                        print(f"Computer does checkmate with {piece} from ({r},{c}) to ({mr},{mc})")
                        return True

    # Paso 2: Si no hay mate en 1, evalúa jugadas normalmente
    best_val = float('-inf')
    best_move = None

    # Get all possible white moves
    all_white_moves = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.startswith('w'):
                moves = get_king_moves(board, r, c, True) if piece == 'w_king' else get_queen_moves(board, r, c)
                for mr, mc in moves:
                    # Add a simple heuristic for move ordering: prioritize captures
                    is_capture = (board[mr][mc] == 'b_king')
                    all_white_moves.append((is_capture, r, c, mr, mc, piece))

    # Sort moves for the root node: captures first
    all_white_moves.sort(key=lambda x: x[0], reverse=True)

    # Depth for the main search
    SEARCH_DEPTH = 4 # Puedes ajustar esto

    for move_info in all_white_moves:
        is_capture, r, c, mr, mc, piece = move_info

        newb = [row[:] for row in board]
        newb[mr][mc] = piece
        newb[r][c] = ''

        # Call minimax for the opponent's turn (minimizing)
        val = minimax(newb, SEARCH_DEPTH - 1, float('-inf'), float('inf'), False)

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

# --- Drawing Functions (existing) ---
def draw_board(win, board, selected=None, valid_moves=[]):
    for r in range(8):
        for c in range(8):
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            if selected == (r, c):
                color = SELECTED_SQUARE
            pygame.draw.rect(win, color, (c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    for (r, c) in valid_moves:
        center = (c * SQUARE_SIZE + SQUARE_SIZE//2, r * SQUARE_SIZE + SQUARE_SIZE//2)
        pygame.draw.circle(win, VALID_MOVE_COLOR, center, 10)

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

def draw_game_state(win, message):
    text = FONT.render(message, True, (0, 0, 0))
    win.blit(text, (10, HEIGHT - 40))

# --- Main Game Loop (existing, with minor adjustments for thread) ---
def main():
    board = init_board()
    turn = 'player'
    selected = None
    game_over = False
    message = ""
    clock = pygame.time.Clock()
    valid_moves = []

    # Clear transposition table at the start of a new game
    TRANSPOSITION_TABLE.clear()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = init_board()
                    turn = 'player'
                    selected = None
                    valid_moves = []
                    game_over = False
                    message = ""
                    TRANSPOSITION_TABLE.clear() # Clear table on restart

            elif event.type == pygame.MOUSEBUTTONDOWN and turn == 'player' and not game_over:
                mx, my = pygame.mouse.get_pos()
                c, r = mx // SQUARE_SIZE, my // SQUARE_SIZE

                if selected is None:
                    if board[r][c] == 'b_king':
                        selected = (r, c)
                        valid_moves = get_black_king_moves(board)
                else:
                    if (r, c) in valid_moves:
                        sr, sc = selected
                        board[r][c] = 'b_king'
                        board[sr][sc] = ''
                        pygame.display.flip()
                        turn = 'computer'
                    selected = None
                    valid_moves = []

        def computer_turn_thread():
            nonlocal turn
            # Limpia la tabla de transposiciones para cada turno de la computadora
            # para evitar que valores de búsqueda profunda de turnos anteriores
            # afecten la búsqueda del turno actual (pueden ser estados "obsoletos")
            # Esto es un trade-off, ya que una tabla persistente sería más rápida si el board
            # no cambia mucho, pero en ajedrez los board states cambian significativamente.
            # Para este escenario simple, es mejor limpiar para evitar errores de lógica.
            TRANSPOSITION_TABLE.clear()
            moved = computer_move(board)
            if moved:
                turn = 'player'

        if not game_over and turn == 'computer' and threading.active_count() == 1:
            # Asegurarse de que no hay otro hilo calculando
            threading.Thread(target=computer_turn_thread).start()


        # Verifica estado del juego
        bk = find_piece(board, 'b_king')
        if is_checkmate(board):
            message = "Checkmate! ¡La computadora gana!"
            game_over = True
        elif is_stalemate(board):
            message = "¡Empate por ahogado!"
            game_over = True
        elif bk is None:
            message = "¡El rey negro fue capturado!"
            game_over = True

        draw_board(WINDOW, board, selected, valid_moves)
        draw_pieces(WINDOW, board)
        if message:
            draw_game_state(WINDOW, message + " - Presiona 'R' para reiniciar")
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()