import pygame
from control import *

WHITE = (255, 255, 255) #white
GRAY = (128, 128, 128)  #gray
BLACK = (0,0,0)         #black

colors = {
        "I": (0,255,255),
        "O": (255,255,0),
        "T": (128,0,128),
        "S": (0,255,0),
        "Z": (255,0,0),
        "J": (0,0,255),
        "L": (255, 127, 0),
        "G": GRAY
    }

muted_colors = {
    "I": (204, 255, 255),
    "O": (255,255,204),
    "T": (240, 180, 240),
    "S": (157, 252, 157),
    "Z": (255, 120, 120),
    "J": (101, 101, 252),
    "L": (252, 187, 121)
}

class palette:
    def __init__(self, outer = WHITE, inner = WHITE, grid = GRAY, text = BLACK):
        self.inner = inner
        self.outer = outer
        self.text = text
        self.grid = grid


default = palette()
blues = palette(outer = (65, 111, 236), inner = (209, 235, 235), grid = WHITE, text = WHITE)

h1 =(234,227,218)
h2 = (191,230,239)
h3 = (225,227,245)
h4 = (230,186,221)
h5 = (232,246,239)

holo = palette(h2, h5, h2, BLACK)



#a helper function for draw_board that draws the preview queue to the screen
def draw_preview(tet: Tetris, screen: pygame.display, pal: palette):
    xpos, ypos = 330, 60
    pZoom = 10
    pygame.draw.rect(screen, pal.inner, [xpos - 10, ypos - 10, pZoom * 4 + 10, pZoom * 5 * tet.previewSize + 10])
    for i, bk in enumerate(tet.preview):
        thisBlock = block(bk, x = 1, y = 1 + 5 * i)
        thisIds = thisBlock.get_loc()
        thisColor = colors[thisBlock.name]
        for idX, idY in thisIds:
            pygame.draw.rect(screen, thisColor, [xpos + pZoom * idX + 1, ypos + pZoom * idY + 1,
                                    pZoom-2, pZoom-2])
    return

#draws the game described in Tetris tet to the display screen
def draw_board(tet: Tetris, screen: pygame.display, pal: palette):
    screen.fill(pal.outer)
    pygame.draw.rect(screen, pal.inner, [tet.x, tet.y + tet.zoom * (tet.h - 20), tet.zoom * tet.w, tet.zoom * 20])
    #draw the field
    #TODO: track dirty bits rather than updating everything
    for i in range(4, tet.h):
        for j in range(tet.w):
            pygame.draw.rect(screen, pal.grid, [tet.x + tet.zoom * j, tet.y + tet.zoom * i,
                                            tet.zoom, tet.zoom], 1)
            if tet.field[i][j] != ' ':
                #c = get_color(tet.field[i][j])
                c = colors[tet.field[i][j]]
                pygame.draw.rect(screen, c, 
                                    [tet.x + tet.zoom * j + 1, tet.y + tet.zoom * i + 1,
                                    tet.zoom - 2, tet.zoom - 2])
            
    ids = tet.active_block.get_loc()
    for idx in ids:
        #way slicker than the original imo
        (x, y) = idx
        if True:
        #if not tet.aiMode:
            c = colors[tet.active_block.name] if y >= (tet.h - 20) else muted_colors[tet.active_block.name]
            pygame.draw.rect(screen, c, [tet.x + tet.zoom * x + 1, tet.y + tet.zoom * y + 1,
                                    tet.zoom-2, tet.zoom-2])
    
    #here we update the score, preview, and board evaluation
    font = pygame.font.SysFont('Calibri', 20, True, False)
    scoreText = font.render("Score: " + str(tet.score), True, pal.text)
    
    previewStr = "Up Next: "
    # for blockNum in tet.preview:
    #     blockName = tet.active_block.names[blockNum]
    #     previewStr += blockName + " "
    previewText = font.render(previewStr, True, pal.text)

    # holeCount = solver.countHoles(tet.field)
    # holeText = font.render("Hole Count: " + str(holeCount), True, BLACK)
    
    # optPlacement = solver.checkStates(tet)
    # optText = font.render("Best: " + str(optPlacement), True, BLACK)
    
    # currPlacement = [tet.active_block.curr, tet.active_block.x]
    # currText = font.render("Current: " + str(currPlacement), True, BLACK)
    
    mode = "CPU" if tet.aiMode else "User"
    modeText = font.render(mode + " is playing!", True, pal.text)
    
    screen.blit(scoreText, [20, 20])
    screen.blit(previewText, [300,20])
    screen.blit(modeText, [140, 650])
    #screen.blit(currText, [250, 650])


    draw_preview(tet, screen, pal)
    
    pygame.display.flip()




def play_tetris(ai = False, dig = False):
    if dig:
        succ = 0
        attempts = 0


    pygame.init()
    
    size = (400,700) #TODO- adjust
    screen = pygame.display.set_mode(size)
    
    pygame.display.set_caption("Tetris")
    
    solver = controller()
    
    #END OF INIT STUFF- ON TO THE GAME LOOP
    
    done = False
    clock = pygame.time.Clock()
    fps = 8
    counter = 0
    tet = Tetris(w = 10, h = 28, aiMode = ai, dig = dig)
    while(not done): #while True with a break doesn't let you play again- this is better
        #INVARIANT: THERE IS ALWAYS AN ACTIVE BLOCK
        #print('in the game loop')
        counter += 1
        if counter > 10000:
            counter = 0
        
        if not tet.aiMode and (counter % (fps) == 0):
            tet.soft_drop()
        
        #will need to refactor this stuff into another fn.
        for event in pygame.event.get():
            if event == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN: #TODO: read the keystroke docs
                #which hard drop is more natural- up or space?
                #gonna start w both
                if event.key == pygame.K_LSHIFT:
                    tet.aiMode = not tet.aiMode
                if event.key == pygame.K_SPACE:
                    tet.hard_drop()
                if event.key == pygame.K_UP:
                    tet.hard_drop()
                if event.key == pygame.K_DOWN:
                    tet.soft_drop()
                if event.key == pygame.K_LEFT:
                    tet.left()
                if event.key == pygame.K_RIGHT:
                    tet.right()
                    
                #not sure about these
                if event.key == pygame.K_f:
                    tet.spin()
                if event.key == pygame.K_d:
                    tet.backspin()
                
                if event.key == pygame.K_ESCAPE:
                    #TODO: implement pause functionality
                    done = True
        
        if tet.aiMode:
            solver.fun_solve(tet)

        #if tet.blocks_played % 3 == 1 or not tet.aiMode:
        if True:
            draw_board(tet, screen, holo)

        clock.tick(fps * 2)

        if dig:
            if not "G" in (cell for row in tet.field for cell in row):
                print("dug it in " + str(tet.blocks_played) + " moves")
                succ += 1
                attempts += 1
                tet = Tetris(w = 10, h = 28, aiMode = ai, dig = dig)
                print(str(succ) + " digs in " + str(attempts) + " attempts!")
                print("apply took " + str(solver.applyTime) + " seconds")
                print("count took " + str(solver.countTime) + " seconds")
                print("reset took " + str(solver.resetTime) + " seconds")
                print("eval took " + str(solver.evalTime) + " seconds")

            if tet.state == "loser":
                attempts += 1
                tet = Tetris(w = 10, h = 28, aiMode = ai, dig = dig)
                print(str(succ) + " digs in " + str(attempts) + " attempts!")
        
        elif tet.state == "loser":
            done = True
            print('Your score is: ' + str(tet.score))
    
    #exited the while loop
    pygame.quit()

play_tetris(ai = True, dig = False)