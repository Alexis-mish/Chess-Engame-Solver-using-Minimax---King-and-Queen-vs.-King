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

# Dibujar el tablero
def draw_board(window):
    for row in range(8):
        for col in range(8):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(window, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Dibujar las piezas
def draw_pieces(window, board):
    font = pygame.font.SysFont('segoeuisymbol', 80)  # Usar fuente compatible con Unicode
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
    global board, removable_pieces, last_remove_time
    board = initialize_board()
    removable_pieces = get_removable_pieces(board)
    last_remove_time = pygame.time.get_ticks()

# Actualizar el tablero eliminando piezas
def update_loop():
    global board, removable_pieces, last_remove_time
    current_time = pygame.time.get_ticks()
    # Eliminar una pieza cada 1000 ms (1 segundo)
    if current_time - last_remove_time >= 100 and removable_pieces:
        row, col = random.choice(removable_pieces)
        board[row][col] = ''  # Eliminar la pieza
        removable_pieces.remove((row, col))  # Quitar de la lista
        last_remove_time = current_time
    draw_board(WINDOW)
    draw_pieces(WINDOW, board)
    pygame.display.flip()

# Función principal
async def main():
    setup()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = mouse_x // SQUARE_SIZE
                row = mouse_y // SQUARE_SIZE
                print(f"Clicked square: ({row}, {col}) - Piece: {board[row][col]}")
        update_loop()
        await asyncio.sleep(1.0 / 60)  # 60 FPS

# Ejecutar según la plataforma
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())