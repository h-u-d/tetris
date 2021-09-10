import copy
import time
from skeleton import *


class controller:
    
    def __init__(self, depth = 1):
        self.depth = depth


    applyTime = 0
    countTime = 0
    resetTime= 0
    evalTime = 0
    move = None

     #given a field, return the highest cell in each row
    def topCells(self, field):
        #turn the field on its side and then find rightmost non-empty cell in each row?
        #probably O(h * w) for all approaches
        w, h = len(field[0]), len(field)
        out = [h for i in range(w)]
        for x in range(w):
            for y in range(h):
                if field[y][x] != ' ':
                    out[x] = y
                    break
        return out

    #Heuristic from http://kth.diva-portal.org/smash/get/diva2:815662/FULLTEXT01.pdf
    #3 rules, count how many cells violate each one- note a cell can be double or triple counted
    def countHoles(self, b: Board):
        #countStart = time.time()

        #only consider y >= max(tops)

        w, h = len(b.field[0]), len(b.field)
        count1, count2, count3 = 0,0,0
        tops = b.tops
        for y in range(min(tops), b.h):
            for x in range(b.w):
                if b.field[y][x] == ' ':
                    if x < w-1 and tops[x+1] <= y: #rule 1
                        count1+= (h-y)
                    if x > 0 and tops[x-1] <= y: #rule 2
                        count2+= (h-y)
                    if tops[x] < y: #rule 3
                        #count3 += (h-y) ** 2
                        count3 += (h - tops[x])
                    if y > 0 and b.field[y-1][x] != ' ': #my digging rule!
                        count3+= (h-y)
        #return count1 + count2 + count3
        out = min(count1, count2) + count1 + count2 + count3

        #self.countTime += time.time() - countStart
        return out
    

    #returns all the places we can put the active block
    #might not need the deepcopy but we'll see
    def genStates(self, b: Board):
        working = copy.deepcopy(b)
        options = []
        if working.active_block == None:
            return options
        for rot in range(len(working.active_block.rotations)):
            for x in range(working.w):
                working.active_block.curr = rot
                working.active_block.x = x
                if not working.intersect():
                    pair = [rot, x]
                    options.append(pair)
        #print(options)
        return options



    ################# THIS CODE IS REPLACED BY recCheck ##########################

    # #generate a tree of possible states given the active block and the next depth blocks in the queue
    # def stateTree(self, tet, depth):

    #     model = copy.deepcopy(tet)
        
    #     #listing ways to place the active block
    #     out = []
    #     first = self.genStates(tet)
    #     for f in first:
    #         out.append([f])


    #     #now we consider the queue!
    #     #what an ugly bit of code
    #     for i in range(depth):
    #         nextOut = []
    #         for seq in out:
    #             seqList = []
    #             self.applySeq(tet, seq)
    #             options = self.genStates(tet)
    #             self.reset(tet, model)
    #             for opt in options:
    #                 seqList += [seq + [opt]]
    #             nextOut += seqList
    #         out = nextOut
    #     return out


    # #Generates a state tree of the prescribed depth, then returns the optimal move sequence
    # def checkStates(self, tetris):
    #     model = tetris
    #     working = copy.deepcopy(tetris)

    #     minHeight = min(self.topCells(tetris.field))
    #     if False:
    #         self.depth = 0
    #     else:
    #         self.depth = 1

    #     options = self.stateTree(working, self.depth)

    #     bestSeq = []
    #     bestHoles = 999999999 #this HAS to be big enough lol


    #     for seq in options:
    #         self.applySeq(working, seq)
    #         holes = self.countHoles(working)
    #         if holes < bestHoles and working.state != "loser":
    #             bestHoles = holes
    #             bestSeq = seq
    #         self.reset(working, model)

    #     return bestSeq



    #a recursive function to evaluate all the options and return the best move
    #returns bestMove, bestScore
    def recCheck(self, b: Board, nLeft: int):
        if nLeft == 0:
            return self.countHoles(b), []
        else:
            working = copy.deepcopy(b)
            #recursive call!
            options = self.genStates(working)
            bestScore = 9999999
            bestMove = []
            for o in options:
                self.apply(working, o)
                score, move = self.recCheck(working, nLeft - 1)
                if score < bestScore and working.state != "loser":
                    bestScore = score
                    bestMove = o
                self.reset(working, b)
            return bestScore, bestMove

    
    
    
    #given a target Board tgt, reset its state to that of the model
    def reset(self, tgt: Board, model: Board):
        #resetStart = time.time()

        #reset the field
        for i in range(model.h):
            for j in range(model.w):
                tgt.field[i][j] = model.field[i][j]

        #reset tops
        for x in range(model.w):
            tgt.tops[x] = model.tops[x]

        #reset the state
        tgt.state = model.state
        

        #reset the active block
        tgt.active_block = block(model.active_block.type)
        
        #reset the preview
        tgtPreview = []
        for bk in model.preview:
            tgtPreview.append(bk)
        tgt.preview = tgtPreview

        #self.resetTime += time.time() - resetStart




    #apply the move described in opt to the Tetris object tetris
    #returns the number of lines cleared
    def apply(self, b: Board, move):
        #applyStart = time.time()
        rot, x = move
        b.active_block.curr = rot
        b.active_block.x = x
        clears = b.fast_drop()
        #self.applyTime += time.time() - applyStart
        return clears
    

    def fun_apply(self, tetris: Tetris):
        #print("move is " + str(move) + " and active block is " + b.active_block.name)
        b = tetris.board
        move = self.move
        rot, x = move
        b.active_block.curr = rot
        if b.active_block.x != x:
            if b.active_block.x > x:
                b.active_block.x -= 1
            else:
                b.active_block.x += 1
            b.soft_drop()
        else:
            self.move = None
            b.hard_drop()

    #prettier, slower version of the solver
    def fun_solve(self, tetris):
        # if not tetris.move:
        #     tetris.move = self.checkStates(tetris, depth)[0]
        b = tetris.board
        if not self.move:
            evalStart = time.time()
            temp = self.recCheck(b, self.depth + 1)[1]
            #temp = self.checkStates(tetris)[0]
            self.evalTime += time.time() - evalStart
            if temp: 
                self.move = temp
        if self.move:
            self.fun_apply(tetris)
        else:
            b.fast_drop()
            

    def solve(self, tetris):
        b = tetris.board
        #evalStart = time.time()
        temp = self.recCheck(b, self.depth + 1)[1]
        #self.evalTime += time.time() - evalStart
        if temp:
            cleared = self.apply(b, temp)
            tetris.blocks_played += 1
            if cleared:
                tetris.score += cleared
        else:
            b.fast_drop()
        

# class stateNode:
#     #each node should store its controller, move, board?, and kids
#         def __init__(self, seq: list, tet: Tetris, ctrl: controller):
#             #TODO: stop when we're deep enough
#             self.seq = seq
#             #self.tet = ctrl.apply(tet, opt)
#             #self.ctrl = ctrl
#             if len(seq) == tet.previewSize:
#                 self.kids = None
#             else:
#                 options = ctrl.genStates(tet)
#                 self.kids = []
#                 for opt in options:
#                     nextSeq = seq.append(opt)
#                     self.kids += stateNode(nextSeq, )