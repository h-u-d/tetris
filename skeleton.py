import random

class block:
    shapes = [
        #I block
        [
            [[0,0], [0,-1], [0,1], [0,2]],
            [[0,0], [-1, 0], [1, 0], [2, 0]]
        ],
        #O block
        [
            [[0,0], [0,-1], [1,0], [1,-1]]
        ],
        #T block
        [
            [[0,0], [-1, 0], [0,1], [1,0]],
            [[0,0], [-1, 0], [0,1], [0,-1]],
            [[0,0], [-1, 0], [0,-1], [1,0]],
            [[0,0], [0, -1], [0,1], [1,0]]
        ],
        #S block
        [
            [[0, 0], [0, 1], [-1, 1], [1,0]],
            [[0, 0], [0, -1], [1, 0], [1, 1]]
        ],
        #Z block
        [
            [[0,0], [-1, 0], [0,1], [1, 1]],
            [[0,0], [0, 1], [1, 0], [1, -1]]
        ],
        #J block
        [
            [[0,0], [0,1], [0,-1], [-1, 1]],
            [[0,0], [-1, -1], [-1, 0], [1, 0]],
            [[0,0], [1, -1], [0, 1], [0, -1]],
            [[0,0], [1, 1], [1, 0], [-1, 0]],
        ],
        #L block
        [
            [[0,0], [0,1], [0,-1], [1, 1]],
            [[0,0], [-1, 1], [-1,0], [1,0]],
            [[0,0], [-1, -1], [0, -1], [0, 1]],
            [[0,0], [-1, 0], [1, 0], [1, -1]]
        ]
    ]
    
    names = ["I","O","T","S", "Z", "J", "L"]
             
    
    def __init__(self, bk = -1, x = 5, y = 1):
        if bk == -1:
            self.type = random.randrange(7)
        else:
            self.type = bk
        self.name = self.names[self.type]
        self.rotations = self.shapes[self.type]
        self.curr = 0 #tracks the current rotation of the block
        self.x = x
        self.y = y
        
    def get_loc(self):
        out = []
        for offset in self.rotations[self.curr]:
            idx = [self.x + list(offset)[0], self.y + list(offset)[1]]
            out.append(idx)
        return out
        
    def spin(self): #this works!
        self.curr = (self.curr + 1) % len(self.rotations)
        
    def backspin(self): #DEBUG
        self.curr = (self.curr - 1) % len(self.rotations)




#looking to refactor a little bit out of the Tetris class
class Board:

    previewSize = 3

    def __init__(self, h, w):
        self.w = w #width of the field
        self.h = h #height of the field
        self.field = [[' ' for x in range(w)] for y in range(h)] #int array array
        self.tops = [h for x in range(w)] #int array describing topmost block height in each column
        self.active_block = block() #current block in play
        self.preview = [random.randrange(7) for i in range(self.previewSize)] #blocks that are coming up
        self.state = "start"

    #checks if the current field is a losing one (stacked too high)
    def isLoser(self):
        if min(self.tops) < self.h - 20:
            self.state = "loser"

    def isFull(self, row):
        return ' ' not in row


    #updates the tops array
    def update_tops(self):
        self.tops = [self.h for x in range(self.w)]
        for x in range(self.w):
            for y in range(self.h):
                if self.field[y][x] != ' ':
                    self.tops[x] = y
                    break



    #pop the top block off the preview list and spawn the next one in
    def spawn(self):
        self.active_block = block(self.preview[0])
        self.preview = self.preview[1:] + [random.randrange(7)]


    #checks if a block bk intersects with the board
    def intersect(self):
        ids = self.active_block.get_loc()
        for x,y in ids:
            if x < 0 or x >= self.w:
                return True
            elif y < 0 or y >= self.h:
                return True
            elif self.field[y][x] != ' ':
                return True
        return False
    
    #TODO: merge add_to_field with clear_lines?
    #adds the active block to the field, then clears lines if needed
    def add_to_field(self, do_spawn = True):
        ids = self.active_block.get_loc()
        name = self.active_block.name
        yList = []
        for x,y in ids:
            if y not in yList:
                yList.append(y)

            self.field[y][x] = name
            self.tops[x] = min(self.tops[x],y)
        clears = self.clear_lines(yList)
        self.isLoser()
        if do_spawn:
            self.spawn()
        return clears



    #check if any lines are full and clear them out! returns the number of lines cleared
    def clear_lines(self, yList):
        #think abt how this could be coded with two pointers instead
        count = 0
        bottom, top = self.h - 1, 0
        #bottom, top = max(self.tops), min(self.tops)
        clearList = []
        for y in yList:
            thisRow = self.field[y]
            if self.isFull(thisRow):
                clearList.append(y)
                
        if not clearList:
            return 0
        
        #now, clearList denotes the lines I need to clear out!

        ptr = max(clearList) #start at the bottom
        while ptr >= self.h - 20:
            if ptr in clearList:
                count += 1
            else:
                thisRow = self.field[ptr]
                for x in range(self.w):
                    self.field[ptr + count][x] = thisRow[x]
            ptr -= 1

        self.update_tops()
        return count


    ################## USER CONTROL METHODS #######################

    #tries to spin the active block clockwise
    def spin(self):
        old = self.active_block.curr
        self.active_block.spin()
        if self.intersect():
            self.active_block.curr = old
        
    #tries to spin the active block counterclockwise
    def backspin(self):
        old = self.active_block.curr
        self.active_block.backspin()
        if self.intersect():
            self.active_block.curr = old

    #tries to move the active block one space to the left
    def left(self):
        self.active_block.x -= 1
        if self.intersect():
            self.active_block.x += 1

    #tries to move the active block one space to the right
    def right(self):
        self.active_block.x += 1
        if self.intersect():
            self.active_block.x -= 1

    #soft drops the active block and return the number of lines cleared
    def soft_drop(self, do_spawn = True):
        clears = 0
        self.active_block.y += 1
        if self.intersect():
            self.active_block.y -= 1
            clears = self.add_to_field(do_spawn)
        return clears
            
    #hard drops the active block and returns the number of lines cleared
    def hard_drop(self, do_spawn = True):
        while not self.intersect():
            self.active_block.y += 1
        self.active_block.y -= 1
        clears = self.add_to_field(do_spawn)
        return clears
    #################### END USER CONTROL METHODS #######################



    #bonus method- fills the field for dig mode
    def make_dig(self):
        digHeight = 15
        for y in range(self.h - digHeight, self.h):
            #choose a cell to leave empty
            emptyIdx = random.randrange(self.w)
            for x in range(self.w):
                if x != emptyIdx:
                    self.field[y][x] = "G"

    

class Tetris:
    
    #These parameters place and size the board within the screen
    x = 100
    y = 60
    zoom = 20
    previewSize = 3 #will play around with this but 3 seems fine for now
    
    def __init__(self, h = 28, w = 10, aiMode = False, dig = False):
        self.move = None
        self.score = 0
        self.blocks_played = 0
        self.board = Board(h, w)
        if dig:
            self.board.make_dig()
        self.aiMode = aiMode
    

 
####################################################################
#   below code has been refactored- leaving it here just in case   #
####################################################################

# class OGTetris:
    
#     #These parameters place and size the board within the screen
#     x = 100
#     y = 60
#     zoom = 20
#     previewSize = 3 #will play around with this but 3 seems fine for now
    
#     def __init__(self, w = 10, h = 28, aiMode = False, dig = False):
#         self.move = None
#         self.score = 0
#         self.blocks_played = 0
#         self.state =  "start"
#         self.h = h
#         self.w = w
#         self.field = [[' ' for x in range(w)] for y in range(h)]
#         if dig:
#             self.make_dig()
#         self.active_block = block()
#         self.preview = [random.randrange(7) for i in range(self.previewSize)]
#         self.aiMode = aiMode


#     def make_dig(self):
#         digHeight = 15
#         for y in range(self.h - digHeight, self.h):
#             #choose a cell to leave empty
#             emptyIdx = random.randrange(self.w)
#             for x in range(self.w):
#                 if x != emptyIdx:
#                     self.field[y][x] = "G"

                 
#     def print_board(self):
#         for row in self.field:
#             out = ''
#             for cell in row:
#                 out += cell
#             print(out)
    
#     #switching to a version that calls get_loc() on its own, rather than needing input
#     def intersect(self):
#         ids = self.active_block.get_loc()
#         for [x,y] in ids:
#             if x < 0 or x >= self.w:
#                 return True
#             elif y < 0 or y >= self.h:
#                 return True
#             elif self.field[y][x] != ' ':
#                 return True
#         return False
    
#     #pop the top block off the queue and spawn the next one in
#     def spawn(self):
#         self.active_block = block(self.preview[0])
#         self.preview = self.preview[1:] + [random.randrange(7)]
    
#     #spins the active block (if allowed)
#     def spin(self):
#         old = self.active_block.curr
#         self.active_block.spin()
#         if self.intersect():
#             self.active_block.curr = old
        
#     def backspin(self):
#         old = self.active_block.curr
#         self.active_block.backspin()
#         if self.intersect():
#             self.active_block.curr = old
            
    
#     #moves the active block one space to the left (if allowed)
#     def left(self):
#         self.active_block.x -= 1
#         if self.intersect():
#             self.active_block.x += 1

#     #moves the active block one space to the right (if allowed)
#     def right(self):
#         self.active_block.x += 1
#         if self.intersect():
#             self.active_block.x -= 1
    
#     #soft drops the active block
#     def soft_drop(self, do_spawn = True):
#         self.active_block.y += 1
#         if self.intersect():
#             self.move = None
#             self.active_block.y -= 1
#             self.add_to_field(do_spawn)
            
#     #hard drops the active block
#     def hard_drop(self, do_spawn = True):
#         while not self.intersect():
#             self.active_block.y += 1
#         self.move = None
#         self.active_block.y -= 1
#         self.add_to_field(do_spawn)
        
#     #adds the active block to the field (and spawns a new active block maybe?)
#     def add_to_field(self, do_spawn = True):
#         b = self.active_block
#         for x,y in b.get_loc():
#             self.field[y][x] = b.name
#             if y < (self.h - 20):
#                 self.state = "loser"
#         self.clear_lines()
#         self.blocks_played += 1
#         if do_spawn:
#             self.spawn()
        
    
#     #check if any lines are full and clear them out! returns # of lines cleared
#     def clear_lines(self):
#         #think abt how this could be coded with two pointers instead
#         count = 0
#         y = self.h - 1 #start at the bottom
#         while y >= 0:
#             #TODO: resolve situations with tall stacks
            
#             thisRow = self.field[y]
#             isFull = all(cell != ' ' for cell in thisRow)
#             if isFull:
#                 count += 1
#                 #print('line clear!')
#             else:
#                 for x in range(self.w):
#                     self.field[y + count][x] = thisRow[x]
#             y -= 1
#         self.score += count
    