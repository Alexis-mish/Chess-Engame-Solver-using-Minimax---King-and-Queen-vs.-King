import pygame
import random
import asyncio
import platform

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
WIDTH = 600
HEIGHT = 600
SQUARE_SIZE = WIDTH // 8  # Tamaño de cada casilla (100x100 píxeles)
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game (Unicode)")

# Colores
LIGHT_SQUARE = (240, 217, 181)  # Beige claro
DARK_SQUARE = (181, 136, 99)    # Marrón oscuro
WHITE_PIECE_COLOR = (255, 255, 255)  # Color para piezas blancas
BLACK_PIECE_COLOR = (0, 0, 0)        # Color para piezas negras
SELECTED_SQUARE = (255, 255, 0)      # Amarillo para casilla seleccionada

# Símbolos Unicode para las piezas
PIECES = {
    'w_king': '♔', 'w_queen': '♕', 'w_rook': '♖', 'w_bishop': '♗', 'w_knight': '♘', 'w_pawn': '♙',
    'b_king': '♚', 'b_queen': '♛', 'b_rook': '♜', 'b_bishop': '♝', 'b_knight': '♞', 'b_pawn': '♟'
}

# Inicializar el tablero
def initialize_board():
    board = [
        ['b_rook', 'b_knight', 'b_bishop', 'b_queen', 'b_king', 'b_bishop', 'b_knight', 'b_rook'],
        ['b_pawn' for _ in range(8)],
        ['' for _ in range(8)],
        ['' for _ in range(8)],
        ['' for _ in range(8)],
        ['' for _ in range(8)],
        ['w_pawn' for _ in range(8)],
        ['w_rook', 'w_knight', 'w_bishop', 'w_queen', 'w_king', 'w_bishop', 'w_knight', 'w_rook']
    ]
    return board

# Obtener lista de posiciones de piezas que pueden desaparecer
def get_removable_pieces(board):
    removable = []
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece not in ['b_king', 'w_king', 'w_queen']:
                removable.append((row, col))
    return removable

# Validar movimientos del rey
def get_king_moves(board, row, col):
    moves = []
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]  # 8 direcciones
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 8 and 0 <= new_col < 8 and board[new_row][new_col] == '':
            moves.append((new_row, new_col))
    return moves

# Validar movimientos de la reina
def get_queen_moves(board, row, col):
    moves = []
    # Direcciones: horizontal, vertical, diagonal
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in directions:
        r, c = row, col
        while True:
            r, c = r + dr, c + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == '':
                    moves.append((r, c))
                else:
                    break
            else:
                break
    return moves

# Obtener movimientos válidos para una pieza
def get_valid_moves(board, row, col):
    piece = board[row][col]
    if piece == 'b_king' or piece == 'w_king':
        return get_king_moves(board, row, col)
    elif piece == 'w_queen':
        return get_queen_moves(board, row, col)
    return []

# Mover pieza blanca automáticamente
def computer_move(board):
    white_pieces = []
    for row in range(8):
        for col in range(8):
            if board[row][col] in ['w_king', 'w_queen']:
                white_pieces.append((row, col))
    if not white_pieces:
        return False
    row, col = random.choice(white_pieces)
    moves = get_valid_moves(board, row, col)
    if moves:
        new_row, new_col = random.choice(moves)
        board[new_row][new_col] = board[row][col]
        board[row][col] = ''
        print(f"Computer moved {board[new_row][new_col]} to ({new_row}, {new_col})")
        return True
    return False

# Dibujar el tablero
def draw_board(window, selected_square=None):
    for row in range(8):
        for col in range(8):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            if selected_square == (row, col):
                color = SELECTED_SQUARE
            pygame.draw.rect(window, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Dibujar las piezas
def draw_pieces(window, board):
    font = pygame.font.SysFont('segoeuisymbol', 80)  # Fuente compatible con Unicode
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != '':
                color = WHITE_PIECE_COLOR if piece.startswith('w') else BLACK_PIECE_COLOR
                text = font.render(PIECES[piece], True, color)
                text_rect = text.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                window.blit(text, text_rect)

# Configuración inicial
def setup():
    global board, removable_pieces, last_remove_time, turn, selected_square
    board = initialize_board()
    removable_pieces = get_removable_pieces(board)
    last_remove_time = pygame.time.get_ticks()
    turn = 'player'  # Empieza el jugador (negras)
    selected_square = None

# Actualizar el tablero
def update_loop():
    global board, removable_pieces, last_remove_time, turn, selected_square
    current_time = pygame.time.get_ticks()
    if current_time - last_remove_time >= 100 and removable_pieces:
        row, col = random.choice(removable_pieces)
        board[row][col] = ''
        removable_pieces.remove((row, col))
        last_remove_time = current_time
    elif not removable_pieces and turn == 'computer':
        if computer_move(board):
            turn = 'player'
    draw_board(WINDOW, selected_square)
    draw_pieces(WINDOW, board)
    pygame.display.flip()

# Función principal
async def main():
    global turn, selected_square  # Declarar variables globales
    setup()  # Inicializar el juego
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == 'player' and not removable_pieces:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = mouse_x // SQUARE_SIZE
                row = mouse_y // SQUARE_SIZE
                if selected_square is None:
                    if board[row][col] == 'b_king':
                        selected_square = (row, col)
                        print(f"Selected b_king at ({row}, {col})")
                else:
                    if (row, col) in get_valid_moves(board, *selected_square):
                        board[row][col] = 'b_king'
                        board[selected_square[0]][selected_square[1]] = ''
                        selected_square = None
                        turn = 'computer'
                        print(f"Moved b_king to ({row}, {col})")
                    else:
                        selected_square = None
        update_loop()
        await asyncio.sleep(1.0 / 60)  # 60 FPS

# Ejecutar según la plataforma
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())