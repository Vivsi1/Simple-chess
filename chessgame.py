import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import chess

class ChessGame:
    def __init__(self, root):
        self.board = chess.Board()
        self.root = root
        self.canvas = tk.Canvas(root, width=512, height=512)
        self.selected_square = None
        self.canvas.pack()

        self.piece_images = {
            'K': tk.PhotoImage(file='images/whitek.png'), 'Q': tk.PhotoImage(file='images/whiteq.png'),
            'R': tk.PhotoImage(file='images/whiter.png'), 'B': tk.PhotoImage(file='images/whiteb.png'),
            'N': tk.PhotoImage(file='images/whiten.png'), 'P': tk.PhotoImage(file='images/whitep.png'),
            'k': tk.PhotoImage(file='images/blackk.png'), 'q': tk.PhotoImage(file='images/blackq.png'),
            'r': tk.PhotoImage(file='images/blackr.png'), 'b': tk.PhotoImage(file='images/blackb.png'),
            'n': tk.PhotoImage(file='images/blackn.png'), 'p': tk.PhotoImage(file='images/blackp.png'),
        } #Defines a dictionary for the pieces . Super important to note the capital and the small letters

        self.chessboard()
        self.pieces()

    def chessboard(self):
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 0:
                    color = "antique white"
                else:
                    color = "saddle brown"
                self.canvas.create_rectangle(col * 64, row * 64, (col + 1) * 64, (row + 1) * 64, fill=color) #Fills antique white for odd sqaures in even numbered rows and even squares in odd numbers rows else saddle brown

    def pieces(self):
        self.piece_ids = {}
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is not None:
                piece_char = piece.symbol()
                image = self.piece_images[piece_char]
                col, row = chess.square_file(square), 7 - chess.square_rank(square)
                piece_id = self.canvas.create_image(col * 64 + 32, row * 64 + 32, image=image, tags=(piece_char))
                self.piece_ids[square] = piece_id
                self.canvas.tag_bind(piece_id, "<Button-1>", self.on_click) #32,32 centers the piece . The rest links the ascii board provided by the chess package to the pieces in the GUI

    def on_click(self, event):
        clicked_piece_id = event.widget.find_closest(event.x, event.y)[0] #Takes the first letter of the piece. If its capital the piece is white else black
        square = self.find_square(clicked_piece_id)
        if square is not None:
            self.clear_highlights()
            self.highlight_moves(square)
            self.selected_square = square #This is used to register an event whenever a piece is clicked
            

    def find_square(self, piece_id):
        for square, id_ in self.piece_ids.items():
            if id_ == piece_id:
                return square
        return None

    def highlight_moves(self, square):
        for move in self.board.legal_moves:
            if move.from_square == square:
                dest_col, dest_row = chess.square_file(move.to_square), chess.square_rank(move.to_square)
                dest_col = dest_col
                dest_row = 7 - dest_row
                if self.board.is_capture(move):
                    rectangle_id = self.canvas.create_rectangle(dest_col * 64, dest_row * 64, (dest_col + 1) * 64,(dest_row + 1) * 64, fill="red")
                else:
                    rectangle_id = self.canvas.create_rectangle(dest_col * 64, dest_row * 64, (dest_col + 1) * 64,(dest_row + 1) * 64, fill="coral")
                self.canvas.addtag_withtag("highlight", rectangle_id)
                self.canvas.tag_bind(rectangle_id, "<Button-1>", lambda event, move=move: self.make_move(move))
    
    def make_move(self, move):
        source_piece_id = self.piece_ids.get(self.selected_square)
        if source_piece_id is not None:
            self.canvas.delete(source_piece_id)

        promotion_square = None
        if self.board.piece_at(move.from_square).piece_type == chess.PAWN:
            if chess.square_rank(move.to_square) == 0 or chess.square_rank(move.to_square) == 7:
                promotion_square = move.to_square

        self.board.push(move)

        if promotion_square is not None:
            self.promotion(promotion_square)

        self.clear_highlights()
        self.update_ids()
        self.clear_board()
        self.chessboard()
        self.pieces()

        result = self.board.result()
        if result == "1-0":
            messagebox.showinfo("Game Over", "White wins!")
        elif result == "0-1":
            messagebox.showinfo("Game Over", "Black wins!")
        elif result == "1/2-1/2":
            messagebox.showinfo("Game Over", "The game is a draw.")

    def promotion(self, promotion_square):
        promotion_options = ['Queen', 'Rook', 'Bishop', 'Night']

        promotion = tk.Toplevel(self.root)
        promotion.title("Promotion")

        selected_piece = tk.StringVar()
        selected_piece.set(promotion_options[0])  

        combo = ttk.Combobox(promotion, textvariable=selected_piece, values=promotion_options)
        combo.pack(pady=10)

        def promote():
            promotion_piece = selected_piece.get().lower()  
            promoted_piece = chess.Piece(chess.PIECE_SYMBOLS.index(promotion_piece[0]), not self.board.turn) #Would print the other colour piece without not
            self.board.set_piece_at(promotion_square, promoted_piece)
            self.clear_board()
            self.chessboard()
            self.pieces()
            promotion.destroy()
        promote_button = tk.Button(promotion, text="Promote", command=promote)
        promote_button.pack(pady=10)

        promotion.mainloop()

    def clear_board(self):
        self.canvas.delete("all") #Removes the canvas. Required for updating piece position

    def update_ids(self):
        self.piece_ids.clear()
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
        if piece is not None:
            piece_char = piece.symbol()
            image = self.piece_images[piece_char]
            col, row = chess.square_file(square), 7 - chess.square_rank(square)
            piece_id = self.canvas.create_image(col * 64 + 32, row * 64 + 32, image=image, tags=(piece_char,))
            self.piece_ids[square] = piece_id
            self.canvas.tag_bind(piece_id, "<Button-1>", self.on_click)
            #Updates the piece_ids dictionary. Mainly required for correct positional loading
    
    def clear_highlights(self):
        self.canvas.delete("highlight") 
        #Deletes the highlight. Required for not showing highlights for a piece when another piece is clicked.

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess")
    root.iconphoto(True , tk.PhotoImage(file='images/icon.png'))
    app = ChessGame(root)
    root.mainloop()
