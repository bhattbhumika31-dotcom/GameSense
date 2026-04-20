import sys
import pygame
from connectivity import GameSession

# ── Constants ──────────────────────────────────────────────────────────────────
SQ       = 80          # pixels per square
BOARD_PX = SQ * 8      # 640
WIN_W    = BOARD_PX + 200
WIN_H    = BOARD_PX

# Colours
LIGHT   = (240, 217, 181)
DARK    = (181, 136,  99)
SEL_COL = (246, 246, 105, 180)
DOT_COL = (100, 200,  80, 170)
RING_COL= (200,  80,  40, 170)
LAST_COL= (205, 210,  86, 110)
CHECK_COL=(220,  20,  60, 150)
SIDE_BG = ( 28,  28,  28)
HINT_COL = ( 70, 130, 220, 110)
HINT_RING= ( 70, 130, 220, 180)
BTN_BG   = ( 48,  92, 160)
BTN_EDGE = (125, 175, 240)

# Piece IDs
PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 1,2,3,4,5,6
WHITE, BLACK = 1, -1

PIECE_VAL = {PAWN:1, KNIGHT:3, BISHOP:3, ROOK:5, QUEEN:9, KING:0}

PIECE_MARKS = {
    PAWN: 'P',
    KNIGHT: 'N',
    BISHOP: 'B',
    ROOK: 'R',
    QUEEN: 'Q',
    KING: 'K',
}

UNICODE_GLYPHS = {
    (WHITE,KING):'♔',(WHITE,QUEEN):'♕',(WHITE,ROOK):'♖',
    (WHITE,BISHOP):'♗',(WHITE,KNIGHT):'♘',(WHITE,PAWN):'♙',
    (BLACK,KING):'♚',(BLACK,QUEEN):'♛',(BLACK,ROOK):'♜',
    (BLACK,BISHOP):'♝',(BLACK,KNIGHT):'♞',(BLACK,PAWN):'♟',
}

# Keep GLYPHS ASCII-safe for any future text-based rendering paths.
GLYPHS = {
    (WHITE, KING): 'K', (WHITE, QUEEN): 'Q', (WHITE, ROOK): 'R',
    (WHITE, BISHOP): 'B', (WHITE, KNIGHT): 'N', (WHITE, PAWN): 'P',
    (BLACK, KING): 'K', (BLACK, QUEEN): 'Q', (BLACK, ROOK): 'R',
    (BLACK, BISHOP): 'B', (BLACK, KNIGHT): 'N', (BLACK, PAWN): 'P',
}

def get_chess_suggestion(game):
    """Import the helper lazily so the game still runs as a script."""
    current = sys.modules.get(__name__)
    if current is not None:
        sys.modules.setdefault('chess_game', current)
    from chess_helper import suggest_for_game
    return suggest_for_game(game)

# ── Board helpers ──────────────────────────────────────────────────────────────

def new_board():
    b = [[None]*8 for _ in range(8)]
    back = [ROOK,KNIGHT,BISHOP,QUEEN,KING,BISHOP,KNIGHT,ROOK]
    for c in range(8):
        b[0][c] = (BLACK, back[c])
        b[1][c] = (BLACK, PAWN)
        b[6][c] = (WHITE, PAWN)
        b[7][c] = (WHITE, back[c])
    return b

def on(r,c): return 0<=r<8 and 0<=c<8

def copy_board(b): return [row[:] for row in b]

# ── Move generation ────────────────────────────────────────────────────────────

def pawn_moves(b, r, c, ep):
    color,_ = b[r][c]
    d = -1 if color==WHITE else 1
    sr = 6 if color==WHITE else 1
    mvs=[]
    if on(r+d,c) and b[r+d][c] is None:
        mvs.append((r,c,r+d,c))
        if r==sr and b[r+2*d][c] is None:
            mvs.append((r,c,r+2*d,c))
    for dc in(-1,1):
        nr,nc=r+d,c+dc
        if on(nr,nc):
            if b[nr][nc] and b[nr][nc][0]!=color:
                mvs.append((r,c,nr,nc))
            if ep==(nr,nc):
                mvs.append((r,c,nr,nc))
    return mvs

def slide(b,r,c,dirs):
    color,_=b[r][c]; mvs=[]
    for dr,dc in dirs:
        nr,nc=r+dr,c+dc
        while on(nr,nc):
            t=b[nr][nc]
            if t is None: mvs.append((r,c,nr,nc))
            elif t[0]!=color: mvs.append((r,c,nr,nc)); break
            else: break
            nr+=dr; nc+=dc
    return mvs

def knight_moves(b,r,c):
    color,_=b[r][c]
    return [(r,c,r+dr,c+dc)
            for dr,dc in[(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
            if on(r+dr,c+dc) and (b[r+dr][c+dc] is None or b[r+dr][c+dc][0]!=color)]

def king_raw(b,r,c,cas):
    color,_=b[r][c]; mvs=[]
    for dr in(-1,0,1):
        for dc in(-1,0,1):
            if dr==dc==0: continue
            nr,nc=r+dr,c+dc
            if on(nr,nc) and (b[nr][nc] is None or b[nr][nc][0]!=color):
                mvs.append((r,c,nr,nc))
    if cas:
        if color==WHITE and r==7 and c==4:
            if cas.get('K') and b[7][5] is None and b[7][6] is None:
                mvs.append((7,4,7,6))
            if cas.get('Q') and b[7][3] is None and b[7][2] is None and b[7][1] is None:
                mvs.append((7,4,7,2))
        if color==BLACK and r==0 and c==4:
            if cas.get('k') and b[0][5] is None and b[0][6] is None:
                mvs.append((0,4,0,6))
            if cas.get('q') and b[0][3] is None and b[0][2] is None and b[0][1] is None:
                mvs.append((0,4,0,2))
    return mvs

def raw_moves(b,r,c,ep,cas):
    if b[r][c] is None: return []
    _,p=b[r][c]
    if p==PAWN:   return pawn_moves(b,r,c,ep)
    if p==KNIGHT: return knight_moves(b,r,c)
    if p==BISHOP: return slide(b,r,c,[(-1,-1),(-1,1),(1,-1),(1,1)])
    if p==ROOK:   return slide(b,r,c,[(-1,0),(1,0),(0,-1),(0,1)])
    if p==QUEEN:  return slide(b,r,c,[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)])
    if p==KING:   return king_raw(b,r,c,cas)
    return []

def all_raw(b,color,ep,cas):
    mvs=[]
    for r in range(8):
        for c in range(8):
            if b[r][c] and b[r][c][0]==color:
                mvs.extend(raw_moves(b,r,c,ep,cas))
    return mvs

def find_king(b,color):
    for r in range(8):
        for c in range(8):
            if b[r][c]==(color,KING): return r,c

def in_check(b,color):
    kr,kc=find_king(b,color)
    return any(m[2]==kr and m[3]==kc for m in all_raw(b,-color,None,None))

def do_move(b,m,ep):
    r1,c1,r2,c2=m
    nb=copy_board(b); new_ep=None
    color,piece=nb[r1][c1]
    if piece==PAWN and ep==(r2,c2):          # en-passant capture
        nb[r1][c2]=None
    if piece==PAWN and abs(r2-r1)==2:
        new_ep=((r1+r2)//2,c1)
    if piece==KING and abs(c2-c1)==2:        # castling
        if c2==6: nb[r1][5]=nb[r1][7]; nb[r1][7]=None
        else:     nb[r1][3]=nb[r1][0]; nb[r1][0]=None
    nb[r2][c2]=nb[r1][c1]; nb[r1][c1]=None
    if piece==PAWN and (r2==0 or r2==7):     # auto-queen for now
        nb[r2][c2]=(color,QUEEN)
    return nb,new_ep

def legal_moves(b,color,ep,cas):
    legal=[]
    for m in all_raw(b,color,ep,cas):
        r1,c1,r2,c2=m
        nb,_=do_move(b,m,ep)
        if in_check(nb,color): continue
        # forbid castling through check
        if b[r1][c1] and b[r1][c1][1]==KING and abs(c2-c1)==2:
            step=1 if c2>c1 else -1
            if in_check(b,color): continue
            mid=copy_board(b); mid[r1][c1+step]=b[r1][c1]; mid[r1][c1]=None
            if in_check(mid,color): continue
        legal.append(m)
    return legal

def update_castling(cas,b,m):
    r1,c1,_,_=m; nc=dict(cas)
    cell=b[r1][c1]
    if cell is None: return nc
    color,piece=cell
    if piece==KING:
        if color==WHITE: nc['K']=nc['Q']=False
        else:            nc['k']=nc['q']=False
    if piece==ROOK:
        if color==WHITE:
            if c1==7: nc['K']=False
            if c1==0: nc['Q']=False
        else:
            if c1==7: nc['k']=False
            if c1==0: nc['q']=False
    return nc

# ── Algebraic notation ─────────────────────────────────────────────────────────
FILES='abcdefgh'
PNAMES={PAWN:'',KNIGHT:'N',BISHOP:'B',ROOK:'R',QUEEN:'Q',KING:'K'}

def to_alg(b,m,resulting_board,color):
    r1,c1,r2,c2=m
    cell=b[r1][c1]
    if cell is None: return '?'
    _,p=cell
    cap=b[r2][c2] is not None
    dest=f"{FILES[c2]}{8-r2}"
    if p==KING and abs(c2-c1)==2:
        return 'O-O' if c2==6 else 'O-O-O'
    pre=FILES[c1] if p==PAWN and cap else PNAMES[p]
    cx='x' if cap else ''
    chk=''
    if in_check(resulting_board,-color):
        lm=legal_moves(resulting_board,-color,None,None)
        chk='#' if not lm else '+'
    return f"{pre}{cx}{dest}{chk}"

# ── Game state ─────────────────────────────────────────────────────────────────

class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board    = new_board()
        self.turn     = WHITE
        self.ep       = None
        self.cas      = {'K':True,'Q':True,'k':True,'q':True}
        self.selected = None
        self.sel_moves= []
        self.last_move= None
        self.history  = []   # snapshots for undo
        self.notation = []   # (white_note, black_note) pairs
        self._pending_note = None
        self.status   = 'playing'  # playing / check / checkmate / stalemate
        self.promoting= False
        self.promo_move= None
        self.hint_text = ''
        self.hint_move = None

    def clear_hint(self):
        self.hint_text = ''
        self.hint_move = None

    def _snap(self):
        return (copy_board(self.board), self.ep, dict(self.cas),
                self.turn, list(self.notation), self._pending_note, self.last_move)

    def _restore(self, snap):
        self.board, self.ep, self.cas, self.turn, self.notation, \
            self._pending_note, self.last_move = snap
        self.selected=None; self.sel_moves=[]
        self.promoting=False; self.promo_move=None
        self.clear_hint()
        self._refresh_status()

    def undo(self):
        if len(self.history)<1: return
        self._restore(self.history.pop())

    def click(self, r, c):
        if self.status in ('checkmate','stalemate') or self.promoting:
            return
        cell=self.board[r][c]
        if self.selected is None:
            if cell and cell[0]==self.turn:
                self.selected=(r,c)
                self.sel_moves=[m for m in legal_moves(self.board,self.turn,self.ep,self.cas)
                                if m[0]==r and m[1]==c]
        else:
            targets={(m[2],m[3]):m for m in self.sel_moves}
            if (r,c) in targets:
                move=targets[(r,c)]
                # check promotion
                sr,sc=self.selected
                if self.board[sr][sc] and self.board[sr][sc][1]==PAWN and (r==0 or r==7):
                    self.promoting=True; self.promo_move=move; self.selected=None; self.sel_moves=[]
                else:
                    self._apply(move)
            elif cell and cell[0]==self.turn:
                self.selected=(r,c)
                self.sel_moves=[m for m in legal_moves(self.board,self.turn,self.ep,self.cas)
                                if m[0]==r and m[1]==c]
            else:
                self.selected=None; self.sel_moves=[]

    def promote(self, piece):
        move=self.promo_move
        self.promoting=False; self.promo_move=None
        self._apply(move, promo=piece)

    def _apply(self, move, promo=None):
        self.history.append(self._snap())
        new_cas=update_castling(self.cas,self.board,move)
        nb,new_ep=do_move(self.board,move,self.ep)
        if promo:
            r2,c2=move[2],move[3]
            color=nb[r2][c2][0]
            nb[r2][c2]=(color,promo)
        note=to_alg(self.board,move,nb,self.turn)
        if self.turn==WHITE:
            self._pending_note=note
        else:
            if self._pending_note is not None:
                self.notation.append((self._pending_note, note))
            self._pending_note=None
        self.board=nb; self.ep=new_ep; self.cas=new_cas
        self.last_move=move; self.turn=-self.turn
        self.selected=None; self.sel_moves=[]
        self.clear_hint()
        self._refresh_status()

    def request_hint(self):
        if self.promoting:
            self.hint_text = 'Finish the promotion choice first.'
            self.hint_move = None
            return

        suggestion = get_chess_suggestion(self)
        if suggestion is None:
            self.hint_text = 'No legal move available.'
            self.hint_move = None
            return

        player = 'White' if self.turn == WHITE else 'Black'
        self.hint_move = suggestion['move']
        self.hint_text = f"{player}: {suggestion['text']}. It {suggestion['reason']}."

    def _refresh_status(self):
        lm=legal_moves(self.board,self.turn,self.ep,self.cas)
        if not lm:
            self.status='checkmate' if in_check(self.board,self.turn) else 'stalemate'
        elif in_check(self.board,self.turn):
            self.status='check'
        else:
            self.status='playing'

# ── Renderer ───────────────────────────────────────────────────────────────────

class Renderer:
    def __init__(self, screen):
        self.screen=screen
        pygame.font.init()
        self.pfont=pygame.font.SysFont(None, int(SQ*0.42), bold=True)
        self.sfont=pygame.font.SysFont('Arial',14)
        self.cfont=pygame.font.SysFont('Arial',13,bold=True)
        self.stfont=pygame.font.SysFont('Arial',19,bold=True)
        self.bfont=pygame.font.SysFont('Arial',15,bold=True)

    def _best_piece_font(self):
        return pygame.font.SysFont(None, int(SQ*0.42), bold=True)
        for name in ['segoeuisymbol','notosans','dejavusans','freesans',None]:
            try:
                f=pygame.font.SysFont(name, int(SQ*0.82))
                if f.render('♔',True,(0,0,0)).get_width()>10: return f
            except: pass
        return pygame.font.SysFont(None, int(SQ*0.78))

    def overlay(self, surf, color, r, c, shape='fill'):
        x,y=c*SQ,r*SQ
        s=pygame.Surface((SQ,SQ),pygame.SRCALPHA)
        if shape=='dot':
            pygame.draw.circle(s,color,(SQ//2,SQ//2),SQ//6)
        elif shape=='ring':
            pygame.draw.circle(s,color,(SQ//2,SQ//2),SQ//2-3,5)
        else:
            s.fill(color)
        surf.blit(s,(x,y))

    def hint_button_rect(self):
        return pygame.Rect(BOARD_PX + 15, WIN_H - 110, 170, 34)

    def _wrap_text(self, text, font, width):
        words = text.split()
        if not words:
            return []
        lines = []
        current = words[0]
        for word in words[1:]:
            test = f"{current} {word}"
            if font.size(test)[0] <= width:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def _draw_piece(self, surf, cell, x, y, size=SQ):
        color, piece = cell
        label = PIECE_MARKS.get(piece, '?')
        pad = max(8, size // 8)
        piece_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        token = pygame.Rect(pad, pad, size - 2 * pad, size - 2 * pad)
        shadow = token.move(2, 3)

        if color == WHITE:
            fill = (244, 239, 228)
            rim = (58, 48, 38)
            text = (58, 48, 38)
            gloss = (255, 255, 255)
        else:
            fill = (46, 43, 40)
            rim = (236, 229, 218)
            text = (242, 236, 228)
            gloss = (84, 80, 76)

        pygame.draw.ellipse(piece_surf, (0, 0, 0, 55), shadow)
        pygame.draw.ellipse(piece_surf, fill, token)
        pygame.draw.ellipse(piece_surf, rim, token, 3)

        gloss_rect = pygame.Rect(token.x + 6, token.y + 5, token.w - 12, max(10, token.h // 3))
        pygame.draw.ellipse(piece_surf, gloss, gloss_rect, 1)

        glyph = self.pfont.render(label, True, text)
        gx = (size - glyph.get_width()) // 2
        gy = (size - glyph.get_height()) // 2 - 1
        piece_surf.blit(glyph, (gx, gy))
        surf.blit(piece_surf, (x, y))

    def draw(self, g):
        self.screen.fill((18,18,18))
        bs=pygame.Surface((BOARD_PX,BOARD_PX))
        # squares
        for r in range(8):
            for c in range(8):
                pygame.draw.rect(bs, LIGHT if (r+c)%2==0 else DARK,
                                 (c*SQ,r*SQ,SQ,SQ))
        # last move
        if g.last_move:
            for r,c in[(g.last_move[0],g.last_move[1]),(g.last_move[2],g.last_move[3])]:
                self.overlay(bs,LAST_COL,r,c)
        if g.hint_move:
            hr1,hc1,hr2,hc2=g.hint_move
            self.overlay(bs,HINT_COL,hr1,hc1)
            self.overlay(bs,HINT_COL,hr2,hc2)
            self.overlay(bs,HINT_RING,hr2,hc2,'ring')
        # selected
        if g.selected:
            self.overlay(bs,SEL_COL,*g.selected)
        # legal dots/rings
        for m in g.sel_moves:
            _,_,r2,c2=m
            if g.board[r2][c2]:
                self.overlay(bs,RING_COL,r2,c2,'ring')
            else:
                self.overlay(bs,DOT_COL,r2,c2,'dot')
        # king in check
        if g.status in('check','checkmate'):
            kr,kc=find_king(g.board,g.turn)
            self.overlay(bs,CHECK_COL,kr,kc)
        # pieces
        for r in range(8):
            for c in range(8):
                cell=g.board[r][c]
                if cell is None: continue
                x,y=c*SQ,r*SQ
                self._draw_piece(bs, cell, x, y)
        # coordinates
        for i in range(8):
            f1=DARK  if i%2==0 else LIGHT
            f2=LIGHT if i%2==0 else DARK
            bs.blit(self.cfont.render(FILES[i],True,f1),(i*SQ+SQ-14,BOARD_PX-16))
            bs.blit(self.cfont.render(str(8-i),True,f2),(3,i*SQ+3))
        self.screen.blit(bs,(0,0))
        # sidebar
        self._sidebar(g)
        # status bar
        self._status(g)
        # promotion dialog
        if g.promoting:
            self._promo_dialog(g)

    def _sidebar(self, g):
        sx=BOARD_PX
        pygame.draw.rect(self.screen,SIDE_BG,(sx,0,200,WIN_H))
        title=self.sfont.render('Move History',True,(200,200,200))
        self.screen.blit(title,(sx+10,10))
        pygame.draw.line(self.screen,(70,70,70),(sx,30),(sx+200,30),1)
        y=38; lh=19
        hint_top = WIN_H - 178
        vis=max(0,(hint_top-y-10)//lh)
        pairs=g.notation[:]
        if g._pending_note:
            pairs=pairs+[(g._pending_note,'')]
        start=max(0,len(pairs)-vis)
        for i,(wn,bn) in enumerate(pairs[start:],start+1):
            n=self.sfont.render(f'{i}.',True,(100,100,100))
            w=self.sfont.render(wn,True,(230,230,230))
            b=self.sfont.render(bn,True,(150,150,150))
            self.screen.blit(n,(sx+6,y))
            self.screen.blit(w,(sx+34,y))
            self.screen.blit(b,(sx+104,y))
            y+=lh

        pygame.draw.line(self.screen,(70,70,70),(sx+8,hint_top-8),(sx+192,hint_top-8),1)
        hint_label=self.sfont.render('Suggestion',True,(200,200,200))
        self.screen.blit(hint_label,(sx+10,hint_top))

        hint_text=g.hint_text or 'Press the button for a simple next move.'
        hint_color=(220,220,220) if g.hint_text else (140,140,140)
        for i,line in enumerate(self._wrap_text(hint_text,self.sfont,170)[:4]):
            txt=self.sfont.render(line,True,hint_color)
            self.screen.blit(txt,(sx+10,hint_top+22+i*16))

        btn=self.hint_button_rect()
        pygame.draw.rect(self.screen,BTN_BG,btn,border_radius=6)
        pygame.draw.rect(self.screen,BTN_EDGE,btn,2,border_radius=6)
        blbl=self.bfont.render('Show Suggestion',True,(245,245,245))
        self.screen.blit(blbl,(btn.centerx-blbl.get_width()//2,btn.centery-blbl.get_height()//2))

        for txt,cy in[('U - Undo',WIN_H-38),('R - Restart',WIN_H-20)]:
            self.screen.blit(self.sfont.render(txt,True,(75,75,75)),(sx+8,cy))

    def _status(self, g):
        msgs={
            'checkmate': f"Checkmate! {'Black' if g.turn==WHITE else 'White'} wins!",
            'stalemate': 'Stalemate – Draw!',
            'check':     f"{'White' if g.turn==WHITE else 'Black'} is in Check!",
            'playing':   f"{'White' if g.turn==WHITE else 'Black'} to move",
        }
        clrs={'checkmate':(220,50,50),'stalemate':(200,160,50),
              'check':(220,120,50),'playing':(200,200,200)}
        t=self.stfont.render(msgs[g.status],True,clrs[g.status])
        bg=pygame.Surface((t.get_width()+16,t.get_height()+8),pygame.SRCALPHA)
        bg.fill((0,0,0,160))
        x=(BOARD_PX-bg.get_width())//2
        self.screen.blit(bg,(x,BOARD_PX-bg.get_height()-6))
        self.screen.blit(t,(x+8,BOARD_PX-t.get_height()-10))

    def _promo_dialog(self, g):
        pieces=[QUEEN,ROOK,BISHOP,KNIGHT]
        total=SQ*4; ox=(BOARD_PX-total)//2; oy=(BOARD_PX-SQ)//2
        ov=pygame.Surface((BOARD_PX,BOARD_PX),pygame.SRCALPHA)
        ov.fill((0,0,0,160)); self.screen.blit(ov,(0,0))
        color=g.turn   # it's still g.turn at promotion time
        for i,p in enumerate(pieces):
            x=ox+i*SQ
            pygame.draw.rect(self.screen,(245,245,245),(x,oy,SQ,SQ))
            pygame.draw.rect(self.screen,(80,80,80),(x,oy,SQ,SQ),2)
            self._draw_piece(self.screen, (color, p), x, oy)
        lbl=self.sfont.render('Choose promotion piece',True,(230,230,230))
        self.screen.blit(lbl,((BOARD_PX-lbl.get_width())//2, oy-26))

    def promo_click(self, mx, my, g):
        """Return chosen piece or None."""
        pieces=[QUEEN,ROOK,BISHOP,KNIGHT]
        total=SQ*4; ox=(BOARD_PX-total)//2; oy=(BOARD_PX-SQ)//2
        for i,p in enumerate(pieces):
            if pygame.Rect(ox+i*SQ,oy,SQ,SQ).collidepoint(mx,my):
                return p
        return None

# ── Main ───────────────────────────────────────────────────────────────────────

def sync_session(game, session):
    session.update_moves(len(game.history))
    if game.status == 'checkmate':
        session.record_win(len(game.history))
    elif game.status == 'stalemate':
        session.record_loss(len(game.history))

def main():
    pygame.init()
    screen=pygame.display.set_mode((WIN_W,WIN_H))
    pygame.display.set_caption('Chess – Two Players')
    clock=pygame.time.Clock()
    renderer=Renderer(screen)
    game=Game()
    session=GameSession("Chess")


    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                sync_session(game, session)
                pygame.quit(); sys.exit()

            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_r:
                    session.record_loss(len(game.history))
                    game.reset()
                    session=GameSession("Chess")
                elif event.key==pygame.K_u:
                    game.undo()

            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                mx,my=event.pos
                if mx>=BOARD_PX:
                    if renderer.hint_button_rect().collidepoint(mx,my):
                        game.request_hint()
                    continue

                if game.promoting:
                    piece=renderer.promo_click(mx,my,game)
                    if piece: game.promote(piece)
                else:
                    sq=mx//SQ, my//SQ   # col, row
                    game.click(sq[1], sq[0])

        sync_session(game, session)
        renderer.draw(game)
        pygame.display.flip()

if __name__=='__main__':
    main()
