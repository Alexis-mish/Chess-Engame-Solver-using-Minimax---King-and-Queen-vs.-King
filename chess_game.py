import copy

# Constantes
EMPTY = "."
WHITE_KING = "K"
WHITE_QUEEN = "Q"
BLACK_KING = "k"

BOARD_SIZE = 8

# Crea el tablero inicial con rey y reina blancos vs rey negro
def create_initial_board():
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    board[7][4] = WHITE_KING    # e1
    board[7][3] = WHITE_QUEEN   # d1
    board[0][4] = BLACK_KING    # e8
    return board

# Imprimir el tablero bonito
def print_board(board):
    for row in board:
        print(" ".join(row))
    print()

# Encuentra la posición de una pieza
def find_piece(board, piece):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == piece:
                return (i, j)
    return None

# Movimientos legales del rey (8 direcciones)
def king_moves(pos):
    moves = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            r, c = pos[0] + dr, pos[1] + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                moves.append((r, c))
    return moves

# Movimientos legales de la reina (líneas y diagonales)
def queen_moves(pos, board):
    moves = []
    directions = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    for dr, dc in directions:
        r, c = pos
        while True:
            r += dr
            c += dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if board[r][c] == EMPTY:
                    moves.append((r, c))
                elif board[r][c] == BLACK_KING:
                    break  # No capturar al rey
                else:
                    break
            else:
                break
    return moves

# Aplicar un movimiento
def apply_move(board, piece, new_pos):
    old_pos = find_piece(board, piece)
    if old_pos is None:
        return
    if board[new_pos[0]][new_pos[1]] == BLACK_KING and piece != BLACK_KING:
        return
    board[old_pos[0]][old_pos[1]] = EMPTY
    board[new_pos[0]][new_pos[1]] = piece

# Verificar si una casilla está atacada por la reina o el rey blanco
def is_attacked_by_white(board, r, c):
    wq = find_piece(board, WHITE_QUEEN)
    wk = find_piece(board, WHITE_KING)

    if wq:
        if r == wq[0] or c == wq[1] or abs(r - wq[0]) == abs(c - wq[1]):
            return True
    if wk:
        if abs(r - wk[0]) <= 1 and abs(c - wk[1]) <= 1:
            return True
    return False

# Verificar si el rey negro está en jaque
def is_check(board):
    bk = find_piece(board, BLACK_KING)
    if bk is None:
        return False
    return is_attacked_by_white(board, bk[0], bk[1])

# Verificar si el rey negro está en jaque mate
def is_checkmate(board):
    if not is_check(board):
        return False
    bk = find_piece(board, BLACK_KING)
    for move in king_moves(bk):
        r, c = move
        if board[r][c] != EMPTY:
            continue
        temp_board = copy.deepcopy(board)
        apply_move(temp_board, BLACK_KING, move)
        if not is_check(temp_board):
            return False
    return True

# Evaluar la posición
def evaluate(board):
    wk_pos = find_piece(board, WHITE_KING)
    wq_pos = find_piece(board, WHITE_QUEEN)
    bk_pos = find_piece(board, BLACK_KING)

    if bk_pos is None:
        return -999

    # Penaliza si la reina está justo al lado del rey negro (evita regalarse)
    if abs(wq_pos[0] - bk_pos[0]) <= 1 and abs(wq_pos[1] - bk_pos[1]) <= 1:
        return -500

    distance_king = abs(wk_pos[0] - bk_pos[0]) + abs(wk_pos[1] - bk_pos[1])
    distance_queen = abs(wq_pos[0] - bk_pos[0]) + abs(wq_pos[1] - bk_pos[1])
    coordination = abs(wk_pos[0] - wq_pos[0]) + abs(wk_pos[1] - wq_pos[1])

    if is_checkmate(board):
        return 1000

    # Mientras más cerca estén rey y reina blancos del rey negro, mejor
    return -(distance_king + 0.5 * distance_queen + 0.3 * coordination)

# Minimax
def minimax(board, depth, is_max):
    if depth == 0 or is_checkmate(board):
        return evaluate(board), None

    if is_max:
        best = float('-inf')
        best_move = None

        # IA blanca mueve
        for piece in [WHITE_KING, WHITE_QUEEN]:
            pos = find_piece(board, piece)
            if pos is None:
                continue
            if piece == WHITE_KING:
                moves = king_moves(pos)
            else:
                moves = queen_moves(pos, board)

            for move in moves:
                temp = copy.deepcopy(board)
                apply_move(temp, piece, move)
                score, _ = minimax(temp, depth - 1, False)
                if score > best:
                    best = score
                    best_move = (piece, move)
        return best, best_move
    else:
        best = float('inf')
        bk = find_piece(board, BLACK_KING)
        moves = king_moves(bk)
        best_move = None
        for move in moves:
            r, c = move
            if board[r][c] != EMPTY:
                continue
            temp = copy.deepcopy(board)
            apply_move(temp, BLACK_KING, move)
            if is_check(temp):
                continue
            score, _ = minimax(temp, depth - 1, True)
            if score < best:
                best = score
                best_move = (BLACK_KING, move)
        return best, best_move

# Juego principal
def play():
    board = create_initial_board()

    while True:
        print_board(board)

        if is_checkmate(board):
            print("¡Jaque mate! La IA (blancas) gana.")
            break
        elif is_check(board):
            print("¡Jaque al rey negro!")

        # Turno IA (blancas)
        print("IA (blancas) pensando...")
        _, move = minimax(board, depth=3, is_max=True)
        if move:
            piece, pos = move
            apply_move(board, piece, pos)
        print_board(board)

        if is_checkmate(board):
            print("¡Jaque mate! La IA (blancas) gana.")
            break
        elif is_check(board):
            print("¡Jaque al rey negro!")

        # Turno jugador (rey negro)
        bk = find_piece(board, BLACK_KING)
        moves = king_moves(bk)
        legal_moves = [m for m in moves if board[m[0]][m[1]] == EMPTY]

        # Filtra movimientos ilegales (no meterse a jaque)
        safe_moves = []
        for m in legal_moves:
            temp = copy.deepcopy(board)
            apply_move(temp, BLACK_KING, m)
            if not is_check(temp):
                safe_moves.append(m)

        if not safe_moves:
            print("Sin movimientos legales. ¡Empate o jaque mate!")
            break

        print("Tu turno (rey negro).")
        for i, m in enumerate(safe_moves):
            print(f"{i}: mover a {m}")
        try:
            choice = int(input("Elige movimiento: "))
            apply_move(board, BLACK_KING, safe_moves[choice])
        except:
            print("Entrada inválida. Turno perdido.")

# Ejecutar el juego
play()
