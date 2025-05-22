import tkinter as tk
from tkinter import messagebox

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game - Green and Gray Board")
        self.square_size = 60
        self.rows = 8
        self.cols = 8
        self.width = self.cols * self.square_size
        self.height = self.rows * self.square_size

        # Colors changed to green and gray for better visibility
        self.color1 = "#aad751"  # light green
        self.color2 = "#777777"  # medium gray

        # Unicode chess symbols for black and white pieces
        self.pieces_unicode = {
            'bR': '\u265C', 'bN': '\u265E', 'bB': '\u265D', 'bQ': '\u265B', 'bK': '\u265A', 'bP': '\u265F',
            'wR': '\u2656', 'wN': '\u2658', 'wB': '\u2657', 'wQ': '\u2655', 'wK': '\u2654', 'wP': '\u2659'
        }

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()

        self.play_button = tk.Button(self.root, text="Play", font=("Arial", 16, "bold"), command=self.play_pressed, bg="#228B22", fg="white")
        self.play_button.place(x=self.width//2 - 40, y=self.height//2 - 20, width=80, height=40)

        self.pieces = {}  # key: (row,col) val: piece code like 'wK'
        self.piece_ids = [[None for _ in range(self.cols)] for _ in range(self.rows)]  # canvas text item IDs
        self.selected_piece = None
        self.is_play = False

        self.create_board()
        self.place_pieces_initial()

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def create_board(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.square_size
                y1 = r * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = self.color1 if (r + c) % 2 == 0 else self.color2
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def place_pieces_initial(self):
        piece_placement = [
            ['bR','bN','bB','bQ','bK','bB','bN','bR'],
            ['bP','bP','bP','bP','bP','bP','bP','bP'],
            [None]*8, [None]*8, [None]*8, [None]*8,
            ['wP','wP','wP','wP','wP','wP','wP','wP'],
            ['wR','wN','wB','wQ','wK','wB','wN','wR'],
        ]
        for r in range(self.rows):
            for c in range(self.cols):
                piece = piece_placement[r][c]
                if piece:
                    self.pieces[(r,c)] = piece
                    self.draw_piece(r, c, piece)

    def draw_piece(self, row, col, piece):
        x = col * self.square_size + self.square_size//2
        y = row * self.square_size + self.square_size//2
        symbol = self.pieces_unicode[piece]
        # Set font color: white pieces always light gray (#eeeeee), black pieces always black (#000000)
        if piece[0] == 'w':
            font_color = "#eeeeee"
        else:
            font_color = "#000000"
        if self.piece_ids[row][col]:
            self.canvas.delete(self.piece_ids[row][col])
        text_id = self.canvas.create_text(x, y, text=symbol, font=("Arial Unicode MS", 36), fill=font_color)
        self.piece_ids[row][col] = text_id

    def clear_piece(self, row, col):
        if self.piece_ids[row][col]:
            self.canvas.delete(self.piece_ids[row][col])
            self.piece_ids[row][col] = None
        if (row,col) in self.pieces:
            del self.pieces[(row,col)]

    def play_pressed(self):
        if self.is_play:
            return
        self.is_play = True
        self.play_button.destroy()
        self.fade_out_pieces()

    def fade_out_pieces(self):
        fade_pieces = []
        for pos, piece in self.pieces.items():
            if piece[0] == 'w':
                if piece[1] != 'K':
                    fade_pieces.append(pos)
            else:
                if piece[1] not in ['K', 'Q']:
                    fade_pieces.append(pos)
        self.fade_step(fade_pieces, 0)

    def fade_step(self, fade_pieces, index):
        if index >= len(fade_pieces):
            self.selected_piece = None
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            return
        row, col = fade_pieces[index]
        self.clear_piece(row, col)
        self.root.after(80, lambda: self.fade_step(fade_pieces, index+1))

    def on_canvas_click(self, event):
        if not self.is_play:
            return
        col = event.x // self.square_size
        row = event.y // self.square_size
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return
        if self.selected_piece is None:
            if (row,col) in self.pieces:
                self.selected_piece = (row,col)
                self.highlight_square(row, col)
        else:
            from_pos = self.selected_piece
            to_pos = (row,col)
            if self.is_valid_move(from_pos, to_pos):
                self.move_piece(from_pos, to_pos)
            else:
                messagebox.showinfo("Invalid Move", "That move is not allowed.")
            self.selected_piece = None
            self.redraw_board_highlight()

    def highlight_square(self, row, col):
        self.redraw_board_highlight()
        x1 = col * self.square_size
        y1 = row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size
        self.highlight_rect = self.canvas.create_rectangle(x1,y1,x2,y2,outline="red", width=3)

    def redraw_board_highlight(self):
        self.canvas.delete("highlight")
        if hasattr(self, 'highlight_rect'):
            self.canvas.delete(self.highlight_rect)
            del self.highlight_rect

    def move_piece(self, from_pos, to_pos):
        piece = self.pieces.get(from_pos)
        if not piece:
            return
        if to_pos in self.pieces:
            self.clear_piece(to_pos[0], to_pos[1])
        self.pieces[to_pos] = piece
        del self.pieces[from_pos]
        self.clear_piece(from_pos[0], from_pos[1])
        self.draw_piece(to_pos[0], to_pos[1], piece)

    def is_valid_move(self, from_pos, to_pos):
        piece = self.pieces.get(from_pos)
        if not piece:
            return False
        r2, c2 = to_pos
        if not (0 <= r2 < 8 and 0 <= c2 < 8):
            return False
        dest_piece = self.pieces.get(to_pos)
        if dest_piece and dest_piece[0] == piece[0]:
            return False
        r1, c1 = from_pos

        if piece[1] == 'K':
            if abs(r2 - r1) <= 1 and abs(c2 - c1) <= 1:
                for dr in [-1,0,1]:
                    for dc in [-1,0,1]:
                        rr = r2 + dr
                        cc = c2 + dc
                        if (rr, cc) in self.pieces and self.pieces[(rr, cc)][1] == 'K' and self.pieces[(rr, cc)][0] != piece[0]:
                            return False
                return True
            return False

        if piece[1] == 'Q':
            dr = r2 - r1
            dc = c2 - c1
            if dr == 0:
                step = 1 if dc > 0 else -1
                for c in range(c1 + step, c2, step):
                    if (r1, c) in self.pieces:
                        return False
                return True
            elif dc == 0:
                step = 1 if dr > 0 else -1
                for r in range(r1 + step, r2, step):
                    if (r, c1) in self.pieces:
                        return False
                return True
            elif abs(dr) == abs(dc):
                step_r = 1 if dr > 0 else -1
                step_c = 1 if dc > 0 else -1
                r, c = r1 + step_r, c1 + step_c
                while (r, c) != (r2, c2):
                    if (r, c) in self.pieces:
                        return False
                    r += step_r
                    c += step_c
                return True
            else:
                return False
        return False

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()

