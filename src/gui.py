"""
Name: Josh Longo and Kevin Shi
Filename: gui.py
Description: Pygame GUI for Expectigammon. Supports AI vs AI and Human vs AI modes.
"""

import pygame
import sys
from src.gammon import Gammon
from src.expectigammon import Player

# Global variables for gui layout and hyperaparameters
WIDTH, HEIGHT = 1150, 720
# Updated to 60 to leave room for point labels
BOARD_X, BOARD_Y = 50, 60
BOARD_W, BOARD_H = 720, 580
BAR_W = 44
# Width of one side (left or right) is half the board width minus the bar, divided by 6 points per side
HALF_W = (BOARD_W - BAR_W) // 2   
# Width of each triangle point, used for click detection and drawing
POINT_W = HALF_W // 6              
PIECE_R = 20
INFO_X = 880
DEPTH = 2
MOVES_CAP = 5
# Create the bear off zones
BEAROFF_X = BOARD_X + BOARD_W + 1
BEAROFF_W = 40
BEAROFF_H = BOARD_H // 2 
WHITE_BEAROFF_RECT = pygame.Rect(BEAROFF_X, BOARD_Y, BEAROFF_W, BEAROFF_H)
BLACK_BEAROFF_RECT = pygame.Rect(BEAROFF_X, BOARD_Y + BOARD_H // 2, BEAROFF_W, BEAROFF_H)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREAM = (245, 235, 200)
DARK_BROWN = (101, 67, 33)
MID_BROWN = (160, 100, 50)
LIGHT_TAN = (210, 180, 140)
RED = (180, 50, 50)
BLUE_GRAY = (100, 120, 160)
GREEN= (50, 140, 80)
HIGHLIGHT = (255, 220, 50)
GRAY = (180, 180, 180)
DARK_GRAY = (80, 80, 80)
BG = (40, 30, 20)


class GUI:
    def __init__(self, mode="ai_vs_ai"):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Expectigammon")
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_md = pygame.font.SysFont("Arial", 17)
        self.font_sm = pygame.font.SysFont("Arial", 13)

        # "ai_vs_ai" or "human_vs_ai"
        self.mode = mode  
        self.game = Gammon()
        self.player1 = Player(1)
        self.player2 = Player(-1)
        self.turn = 0
        self.winner = None
        self.last_roll = None
        self.last_move_lines = ["-"]
        self.last_score = None
        if self.mode == "human_vs_ai":
            self.message = "Press Roll Dice to start."
        else:
            self.message = "Press Next Turn to start."
        # selected point index for human
        self.selected = None     
        # valid moves for human   
        self.valid_moves = []  
        # current roll for human turn     
        self.human_roll = None   
        # remaining dice for human turn   
        self.human_remaining = [] 
        self.human_moves = []
        # waiting for human to move  
        self.waiting_human = False  
        self.btn_rect = pygame.Rect(INFO_X, HEIGHT - 150, 180, 44)
        self.ng_rect = pygame.Rect(INFO_X, HEIGHT - 90, 180, 44)

    @staticmethod
    def convert_move(moveset):
        """Convert a moveset tuple (from index, to index, die used) to human-readable
        strings using point numbers 1-24.  Returns a list of display lines."""
        if not moveset:
            return ["-"]
        lines = []
        for move in moveset:
            frm, to, die = move
            frm_label = "Bar" if frm in (24, 25) else str(frm + 1)
            to_label = "Off" if to in (26, 27) else str(to + 1)
            lines.append(f"{frm_label} to {to_label} (die {die})")
        return lines
    
    @staticmethod
    def wrap_text(text, font, max_width):
        """Wrap text to fit within a max width when rendered with the given font."""
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    # Board geometry helpers
    def col_cx(self, col: int) -> int:
        """Return the horizontal center of column col (0-11). Columns 0-5 
        is left half and columns 6-11 is right half (after bar)."""
        if col < 6:
            return BOARD_X + col * POINT_W + POINT_W // 2
        else:
            return BOARD_X + 6 * POINT_W + BAR_W + (col - 6) * POINT_W + POINT_W // 2

    def point_to_pixel(self, idx: int):
        """Return (cx, cy) of the triangle tip for board index idx."""
        # top row, indices 12-23
        if idx >= 12:         
            col = idx - 12
            return (self.col_cx(col), BOARD_Y + BOARD_H - 20)
        # bottom row indices 11-0 (col 0 = idx 11)
        else:                  
            col = 11 - idx
            return (self.col_cx(col), BOARD_Y + 20)

    def piece_positions(self, idx, count):
        """Return list of (cx, cy) for each piece on a point."""
        base_x, base_y = self.point_to_pixel(idx)
        positions = []
        for i in range(abs(count)):
            # top row, pieces grow downward
            if idx >= 12:  
                cy = BOARD_Y + PIECE_R + i * (PIECE_R * 2 + 2)
            # bottom row, pieces grow upward
            else:          
                cy = BOARD_Y + BOARD_H - PIECE_R - i * (PIECE_R * 2 + 2)
            positions.append((base_x, cy))
        return positions

    def bar_positions(self, player, count):
        """Return list of (cx, cy) for pieces on the bar."""
        bar_cx = BOARD_X + 6 * POINT_W + BAR_W // 2
        positions = []
        for i in range(count):
            if player == 1:
                cy = BOARD_Y + BOARD_H // 2 + 28 + i * (PIECE_R * 2 + 2)
            else:
                cy = BOARD_Y + BOARD_H // 2 - 28 - i * (PIECE_R * 2 + 2)
            positions.append((bar_cx, cy))
        return positions

    # The drawing functions
    def draw_board(self):
        self.screen.fill(BG)
        board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_W, BOARD_H)
        pygame.draw.rect(self.screen, DARK_BROWN, board_rect, border_radius=6)
        pygame.draw.rect(self.screen, MID_BROWN, board_rect, 3, border_radius=6)

        # Draw triangles
        for col in range(12):
            cx = self.col_cx(col)
            color = RED if col % 2 == 0 else LIGHT_TAN

            # Top triangle tip points downward
            tip_y = BOARD_Y + BOARD_H // 2 - 8
            pts_t = [(cx - POINT_W // 2, BOARD_Y),
                     (cx + POINT_W // 2, BOARD_Y),
                     (cx, tip_y)]
            pygame.draw.polygon(self.screen, color, pts_t)
            pygame.draw.polygon(self.screen, DARK_BROWN, pts_t, 1)

            # Bottom triangle tip points upward
            tip_y2 = BOARD_Y + BOARD_H // 2 + 8
            pts_b = [(cx - POINT_W // 2, BOARD_Y + BOARD_H),
                     (cx + POINT_W // 2, BOARD_Y + BOARD_H),
                     (cx, tip_y2)]
            pygame.draw.polygon(self.screen, color, pts_b)
            pygame.draw.polygon(self.screen, DARK_BROWN, pts_b, 1)

        # Bar overlay
        bar_rect = pygame.Rect(BOARD_X + 6 * POINT_W, BOARD_Y, BAR_W, BOARD_H)
        pygame.draw.rect(self.screen, MID_BROWN,  bar_rect)
        pygame.draw.rect(self.screen, DARK_BROWN, bar_rect, 2)

        # Bear off zones
        pygame.draw.rect(self.screen, MID_BROWN, WHITE_BEAROFF_RECT, border_radius=4)
        pygame.draw.rect(self.screen, DARK_BROWN, WHITE_BEAROFF_RECT, 2, border_radius=4)
        pygame.draw.rect(self.screen, MID_BROWN, BLACK_BEAROFF_RECT, border_radius=4)
        pygame.draw.rect(self.screen, DARK_BROWN, BLACK_BEAROFF_RECT, 2, border_radius=4)
        white_label = self.font_sm.render("White", True, CREAM)
        black_label = self.font_sm.render("Black", True, CREAM)
        # Place white label above and black label below
        self.screen.blit(white_label, (WHITE_BEAROFF_RECT.centerx - white_label.get_width() // 2, BOARD_Y - white_label.get_height() - 3))
        self.screen.blit(black_label, (BLACK_BEAROFF_RECT.centerx - black_label.get_width() // 2, BOARD_Y + BOARD_H + 3))

        # Point number labels drawn outside the board (above top edge, below bottom edge)
        for col in range(12):
            cx = self.col_cx(col)
            # index 12-23
            top_idx = 12 + col   
            # index 11-0      
            bot_idx = 11 - col          
            top_pt = top_idx + 1
            bot_pt = bot_idx + 1
            t_surf = self.font_sm.render(str(top_pt), True, CREAM)
            b_surf = self.font_sm.render(str(bot_pt), True, CREAM)
            # above board
            self.screen.blit(t_surf, (cx - t_surf.get_width() // 2,
                                      BOARD_Y - t_surf.get_height() - 3))
            # below board
            self.screen.blit(b_surf, (cx - b_surf.get_width() // 2,
                                      BOARD_Y + BOARD_H + 3))
            
    def draw_pieces(self):
        board = self.game.state.board

        # Highlight selected point
        if self.selected is not None and self.selected < 24:
            positions = self.piece_positions(self.selected, board[self.selected])
            if positions:
                # highlight the top piece on the selected point
                hx, hy = positions[0] 
                pygame.draw.circle(self.screen, HIGHLIGHT, (hx, hy), PIECE_R + 4, 3)

        # Highlight valid destination points
        for vm in self.valid_moves:
            if vm[1] == 26:
                # Highlight white bear off zone
                pygame.draw.rect(self.screen, GREEN, WHITE_BEAROFF_RECT, 3, border_radius=4)
            elif vm[1] == 27:
                # Highlight black bear off zone
                pygame.draw.rect(self.screen, GREEN, BLACK_BEAROFF_RECT, 3, border_radius=4)
            # only highlight on-board destinations not bearing off
            elif vm[1] < 24:  
                val = board[vm[1]]
                if val != 0:
                    position = self.piece_positions(vm[1], val)
                    hx, hy = position[0]
                    # Color red if its opponent blot to hit
                    color = RED if val == -1 else GREEN
                else: 
                    # For empty point highlight where the piece would go
                    hx, _ = self.point_to_pixel(vm[1])
                    # Top row the first piece sits near the top edge
                    if vm[1] >= 12:
                        hy = BOARD_Y + PIECE_R
                    else:
                        hy = BOARD_Y + BOARD_H - PIECE_R
                    color = GREEN
                pygame.draw.circle(self.screen, color, (hx, hy), POINT_W // 2, 3)

        # Draw pieces on points
        for idx in range(24):
            val = board[idx]
            if val == 0:
                continue
            color = CREAM if val > 0 else DARK_GRAY
            border = BLACK if val > 0 else WHITE
            positions = self.piece_positions(idx, val)
            for i, (cx, cy) in enumerate(positions):
                pygame.draw.circle(self.screen, color, (cx, cy), PIECE_R)
                pygame.draw.circle(self.screen, border, (cx, cy), PIECE_R, 2)
                if i == 0 and abs(val) > 1:
                    label = self.font_sm.render(str(abs(val)), True, border)
                    self.screen.blit(label, (cx - label.get_width() // 2, cy - label.get_height() // 2))

        # Bar pieces
        p1_bar = board[24]
        p2_bar = board[25]
        for cx, cy in self.bar_positions(1, p1_bar):
            pygame.draw.circle(self.screen, CREAM, (cx, cy), PIECE_R)
            pygame.draw.circle(self.screen, BLACK, (cx, cy), PIECE_R, 2)
        for cx, cy in self.bar_positions(-1, p2_bar):
            pygame.draw.circle(self.screen, DARK_GRAY, (cx, cy), PIECE_R)
            pygame.draw.circle(self.screen, WHITE, (cx, cy), PIECE_R, 2)

        # Draw bear off pieces in the bear off zones
        piece_h = 10
        piece_gap = 2
        # White pieces
        for i in range(board[26]):
            py = WHITE_BEAROFF_RECT.top + 1 + i * (piece_h + piece_gap)
            pygame.draw.rect(self.screen, CREAM, (WHITE_BEAROFF_RECT.x + 2, py, BEAROFF_W - 4, piece_h), border_radius=4)
            pygame.draw.rect(self.screen, BLACK, (WHITE_BEAROFF_RECT.x + 2, py, BEAROFF_W - 4, piece_h), 1, border_radius=4)
        # Black pieces
        for i in range(board[27]):
            py = BLACK_BEAROFF_RECT.bottom - (i + 1) * (piece_h + piece_gap)
            pygame.draw.rect(self.screen, DARK_GRAY, (BLACK_BEAROFF_RECT.x + 2, py, BEAROFF_W - 4, piece_h), border_radius=4)
            pygame.draw.rect(self.screen, WHITE, (BLACK_BEAROFF_RECT.x + 2, py, BEAROFF_W - 4, piece_h), 1, border_radius=4)


    def draw_info(self):
        board = self.game.state.board
        x, y = INFO_X, 50
        # max text width for wrapping
        max_width = INFO_X - 10

        # Title
        title = self.font_lg.render("Expectigammon", True, CREAM)
        self.screen.blit(title, (x, y)) 
        y += 35

        # Mode
        mode_str = "AI vs AI" if self.mode == "ai_vs_ai" else "Human (White) vs AI (Black)"
        mode_lbl = self.font_md.render(mode_str, True, GRAY)
        self.screen.blit(mode_lbl, (x, y))
        y += 30

        # Turn
        turn_lbl = self.font_md.render(f"Turn: {self.turn + 1}", True, CREAM)
        self.screen.blit(turn_lbl, (x, y))
        y += 30

        # Whose turn
        if not self.winner:
            current = "White" if self.turn % 2 == 0 else "Black"
            color = CREAM if self.turn % 2 == 0 else DARK_GRAY
            who = self.font_md.render(f"To move next: {current}", True, color)
            self.screen.blit(who, (x, y))
        y += 30

        # Roll
        roll_str = str(self.last_roll) if self.last_roll else "-"
        roll_lbl = self.font_md.render(f"Roll: {roll_str}", True, CREAM)
        self.screen.blit(roll_lbl, (x, y))
        y += 35

        # Borne off
        bo_title = self.font_md.render("Borne Off:", True, CREAM)
        self.screen.blit(bo_title, (x, y))
        y += 25
        w_bo = self.font_md.render(f"  White: {board[26]}", True, CREAM)
        self.screen.blit(w_bo, (x, y))
        y += 22
        b_bo = self.font_md.render(f"  Black: {board[27]}", True, DARK_GRAY)
        self.screen.blit(b_bo, (x, y))
        y += 30

        # On bar
        bar_title = self.font_md.render("On Bar:", True, CREAM)
        self.screen.blit(bar_title, (x, y))
        y += 25
        w_bar = self.font_md.render(f"  White: {board[24]}", True, CREAM)
        self.screen.blit(w_bar, (x, y))
        y += 22
        b_bar = self.font_md.render(f"  Black: {board[25]}", True, DARK_GRAY)
        self.screen.blit(b_bar, (x, y))
        y += 30

        # Best move
        move_title = self.font_md.render("Best Move:", True, HIGHLIGHT)
        self.screen.blit(move_title, (x, y))
        y += 22
        for line in self.wrap_text(", ".join(self.last_move_lines), self.font_sm, WIDTH - INFO_X - 10):
            move_lbl = self.font_sm.render(line, True, HIGHLIGHT)
            self.screen.blit(move_lbl, (x, y))
            y += 18

        # Expected value
        if self.last_score is not None:
            y += 4
            score_lbl = self.font_sm.render(f"Expected value: {self.last_score:.2f}", True, HIGHLIGHT)
            self.screen.blit(score_lbl, (x, y))
            y += 18
            note_str = "A positive expected value means an advantage for White, negative means an advantage for Black."
            for line in self.wrap_text(note_str, self.font_sm, WIDTH - INFO_X - 10):
                note = self.font_sm.render(line, True, GRAY)
                self.screen.blit(note, (x, y))
                y += 18
            y += 22

        # Message
        y += 6
        for line in self.wrap_text(self.message, self.font_sm, WIDTH - INFO_X - 10):
            msg = self.font_sm.render(line, True, GRAY)
            self.screen.blit(msg, (x, y))
            y += 18

        # Winner banner
        if self.winner:
            winner_str = "White Wins!" if self.winner == 1 else "Black Wins!"
            banner = self.font_lg.render(winner_str, True, HIGHLIGHT)
            bx = WIDTH // 2 - banner.get_width() // 2
            by = HEIGHT // 2 - banner.get_height() // 2
            pygame.draw.rect(self.screen, DARK_BROWN, 
                             (bx - 10, by - 10, banner.get_width() + 20, banner.get_height() + 20), border_radius=8)
            self.screen.blit(banner, (bx, by))

    def draw_buttons(self):
        pygame.draw.rect(self.screen, BLUE_GRAY, self.btn_rect, border_radius=8)
        pygame.draw.rect(self.screen, MID_BROWN, self.ng_rect,  border_radius=8)
        is_human_turn = self.mode == "human_vs_ai" and self.turn % 2 == 0
        
        btn_text = "Roll Dice" if (is_human_turn and not self.waiting_human) else "Next Turn"
        btn_lbl = self.font_md.render(btn_text, True, WHITE)
        self.screen.blit(btn_lbl, (self.btn_rect.centerx - btn_lbl.get_width() // 2,
                            self.btn_rect.centery - btn_lbl.get_height() // 2))

        ng_lbl = self.font_md.render("New Game", True, WHITE)
        self.screen.blit(ng_lbl, (self.ng_rect.centerx - ng_lbl.get_width() // 2,
                           self.ng_rect.centery - ng_lbl.get_height() // 2))

    def draw(self):
        self.draw_board()
        self.draw_pieces()
        self.draw_info()
        self.draw_buttons()
        pygame.display.flip()

    # Click detection for human moves
    def get_clicked_point(self, mx, my):
        """Return board index if click is near a point, else None."""
        board = self.game.state.board
        for idx in range(24):
            val = board[idx]
            # Check points with pieces first 
            if val != 0:
                positions = self.piece_positions(idx, val)
                for cx, cy in positions:
                    if abs(mx - cx) <= PIECE_R and abs(my - cy) <= PIECE_R:
                        return idx
            # Check empty points for potential move destinations
            else:
                cx = self.col_cx(idx - 12 if idx >= 12 else 11 - idx)
                cy = BOARD_Y + PIECE_R if idx >= 12 else BOARD_Y + BOARD_H - PIECE_R
                if abs(mx - cx) <= POINT_W // 2 and abs(my - cy) <= POINT_W // 2:
                    return idx
        # Check bar area for white pieces
        bar_cx = BOARD_X + 6 * POINT_W + BAR_W // 2
        if abs(mx - bar_cx) <= BAR_W // 2 and BOARD_Y <= my <= BOARD_Y + BOARD_H:
            return 24 if my >= BOARD_Y + BOARD_H // 2 else 25
        # Check bear off zones
        if WHITE_BEAROFF_RECT.collidepoint(mx, my):
            return 26
        if BLACK_BEAROFF_RECT.collidepoint(mx, my):
            return 27
        return None


    # Game logic
    def ai_turn(self):
        """Execute one AI turn."""
        if self.winner:
            return
        current_p = self.player1 if self.turn % 2 == 0 else self.player2
        current_p.take_turn(self.game, depth=DEPTH, moves_cap=MOVES_CAP)

        # Tailored message for no valid moves
        if not current_p.current_move:
            board = self.game.state.board 
            if current_p.player_number == 1 and board[24] > 0:
                self.message = "White has pieces on the bar but can't re-enter — skipping turn."
            elif current_p.player_number == -1 and board[25] > 0:
                self.message = "Black has pieces on the bar but can't re-enter — skipping turn."
            else:
                self.message = "No valid moves — skipping turn."
            self.last_move_lines = ["-"]
        else:
            self.message = ""
            self.last_move_lines = self.convert_move(current_p.current_move)

        # Update display info
        self.last_roll = current_p.current_roll
        if current_p.player_number == -1:
            self.last_score = -current_p.current_score
        else:
            self.last_score = current_p.current_score
        self.turn += 1
        self.winner = self.game.check_winner() or None

    def start_human_turn(self):
        """Roll dice and prepare for human input."""
        if self.winner:
            return
        self.human_roll = self.game.roll_dice()
        self.human_remaining = self.human_roll.copy()
        self.last_roll = self.human_roll
        self.waiting_human = True
        self.selected = None
        self.valid_moves = []
        self.message = f"Click a white piece to select it."

        # Check if any moves exist
        all_moves = self.game.valid_moves(1, self.human_remaining)
        if not all_moves:
            board = self.game.state.board
            if board[24] > 0:
                self.message = "You have pieces on the bar but can't re-enter — skipping turn."
            else:
                self.message = "No valid moves — turn skipped."
            self.last_move_lines = ["-"]
            self.waiting_human = False
            self.turn += 1
            self.winner = self.game.check_winner() or None

    def handle_human_click(self, idx):
        if not self.waiting_human:
            return
        board = self.game.state.board

        # Attempt to complete a move to clicked destination
        if self.selected is not None:
            matching = [vm for vm in self.valid_moves if vm[1] == idx]
            if matching:
                mv = matching[0]
                self.game.make_move(1, mv[0], mv[1], self.human_remaining)
                self.human_remaining.remove(mv[2])
                self.selected = None
                self.valid_moves = []

                if not self.human_remaining or not self.game.valid_moves(1, self.human_remaining):
                    self.waiting_human = False
                    self.turn += 1
                    self.winner = self.game.check_winner() or None
                    self.message = "Press next turn for AI to make a move."
                else:
                    self.message = f"Remaining dice: {self.human_remaining}. Click next piece."
                return

        # Select a piece
        if idx == 24 and board[24] > 0:
            self.selected = 24
            self.valid_moves = [vm for vm in self.game.valid_moves(1, self.human_remaining)
                                if vm[0] == 24]
        elif idx is not None and 0 <= idx < 24 and board[idx] > 0:
            all_v = self.game.valid_moves(1, self.human_remaining)
            self.valid_moves = [vm for vm in all_v if vm[0] == idx]
            self.selected = idx if self.valid_moves else None
            if not self.valid_moves:
                self.message = "No valid moves from that point."
        else:
            self.selected = None
            self.valid_moves = []

    def run(self):
        while True:
            self.clock.tick(30)
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if self.ng_rect.collidepoint(mx, my):
                        # Reset the game state but keep the mode
                        self.__init__(mode=self.mode)  
                        continue

                    if self.btn_rect.collidepoint(mx, my) and not self.winner:
                        if self.mode == "ai_vs_ai":
                            self.ai_turn()
                        else:
                            if self.turn % 2 == 0:
                                if not self.waiting_human:
                                    self.start_human_turn()
                            else:
                                if not self.waiting_human:
                                    self.ai_turn()
                        continue

                    if self.mode == "human_vs_ai" and self.waiting_human:
                        idx = self.get_clicked_point(mx, my)
                        if idx is not None:
                            self.handle_human_click(idx)

def main():
    # Terminal prints prompting user to pick mode
    print("Select mode for Expectigammon:")
    print("1 — AI vs AI")
    print("2 — Human vs AI")
    choice = input("Enter 1 or 2: ").strip()
    mode = "human_vs_ai" if choice == "2" else "ai_vs_ai"
    # Run the game
    GUI(mode).run()
if __name__ == "__main__":
    main()