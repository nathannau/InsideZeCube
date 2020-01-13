import random

class Generator:
    EMPTY = 0
    PIPE = 1
    START = 2
    STOP = 3
    UNUSE = 4

    sizeX = 0
    sizeY = 0
    sizeZ = 0
    cube = []
    paths = {}
    extremities = []

    def __init__(self, sizeX:int, sizeY:int, sizeZ:int):
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.sizeZ = sizeZ
        self.cube = [ Generator.EMPTY] * sizeX *  sizeY * sizeZ
        self.paths = {
            'X': [ False ] * (sizeX-1) *  sizeY * sizeZ,
            'Y': [ False ] * sizeX *  (sizeY-1) * sizeZ,
            'Z': [ False ] * sizeX *  sizeY * (sizeZ-1),
        }        

    def cubePos(self, x:int, y:int, z:int):
        return self.sizeX * self.sizeY * z + self.sizeX * y + x
    def pathXPos(self, x:int, y:int, z:int):
        return (self.sizeX-1) * self.sizeY * z + (self.sizeX-1) * y + x
    def pathYPos(self, x:int, y:int, z:int):
        return self.sizeX * (self.sizeY-1) * z + self.sizeX * y + x
    def pathZPos(self, x:int, y:int, z:int):
        return self.sizeX * self.sizeY * z + self.sizeX * y + x

    def initStart(self, 
        startX1:int, startX2:int, startY:int, 
        stopX1:int, stopX2:int, stopY:int):

        self.extremities = [
            { 'X': startX1-1, 'Y': startY-1, 'Z': 0 },
            { 'X': startX2-1, 'Y': startY-1, 'Z': 0 },
            { 'X': stopX1-1,  'Y': stopY-1,  'Z': self.sizeZ-1 },
            { 'X': stopX2-1,  'Y': stopY-1,  'Z': self.sizeZ-1 },
        ]
        x0 = self.cubePos(0, startY-1, 0)
        for x in range(startX1-1, startX2):
            if x == startX1-1 or x == startX2-1:
                self.cube[x0 + x] = self.START
            else:
                self.cube[x0 + x] = self.UNUSE
        
        x0 = self.cubePos(0, stopY-1, self.sizeZ-1)
        for x in range(stopX1-1, stopX2):
            if x == stopX1-1 or x == stopX2-1:
                self.cube[x0 + x] = self.STOP
            else:
                self.cube[x0 + x] = self.UNUSE

        x0 = self.pathXPos(0, startY-1, 0)
        for x in range(startX1-1, startX2-1):
            self.paths['X'][x0 + x] = True
        x0 = self.pathXPos(0, stopY-1, self.sizeZ-1)
        for x in range(stopX1-1, stopX2-1):
            self.paths['X'][x0 + x] = True

    def copy(self):
        ret = Generator(0, 0, 0)
        ret.sizeX = self.sizeX
        ret.sizeY = self.sizeY
        ret.sizeZ = self.sizeZ
        ret.cube = self.cube[:]
        ret.paths = {
            'X': self.paths['X'][:],
            'Y': self.paths['Y'][:],
            'Z': self.paths['Z'][:],
        }
        ret.extremities = self.extremities[:]
        return ret

    def build(self, 
        startX1:int, startX2:int, startY:int, 
        stopX1:int, stopX2:int, stopY:int,
        seed:int):

        random.seed(seed)
        self.initStart(startX1, startX2, startY, stopX1, stopX2, stopY)

        if random.randint(0, 1) == 0:
            pos = { 'X': startX1-1, 'Y': startY-1, 'Z':0 }
        else:
            pos = { 'X': startX2-1, 'Y': startY-1, 'Z':0 }
             
        self.cube[self.cubePos(pos['X'],pos['Y'], pos['Z'])] = self.PIPE

        return self.buildPath(pos)

    def buildPath(self, pos:dict):

        dirs = [
            { 'X':-1, 'Y':0, 'Z':0 },
            { 'X': 1, 'Y':0, 'Z':0 },
            { 'X':0, 'Y':-1, 'Z':0 },
            { 'X':0, 'Y': 1, 'Z':0 },
            { 'X':0, 'Y':0, 'Z':-1 },
            { 'X':0, 'Y':0, 'Z': 1 },
        ]
        random.shuffle(dirs)

        while len(dirs):
            d = dirs.pop()

            gen = self.setDirection(pos, d)
            if gen is None: continue

            return gen

        return None

    def isValidPosition(self, pos:dict):
        return (pos['X'] >= 0 and pos['Y'] >= 0 and pos['Z'] >= 0 and
                pos['X'] < self.sizeX and pos['Y'] < self.sizeY and pos['Z'] < self.sizeZ)

    def setDirection(self, pos, direction):
        n = dict(pos)
        v = 0
        for k in n: 
            n[k] += direction[k]
            v += direction[k]

        if not self.isValidPosition(n):
            return None

        gen = self.copy()

        ncp = self.cubePos(n['X'], n['Y'], n['Z'])
        if v > 0:
            pp = pos
        else:
            pp = n
        if direction['X'] != 0 : 
            gen.paths['X'][gen.pathXPos(pp['X'], pp['Y'], pp['Z'])] = True
        elif direction['Y'] != 0 : 
            gen.paths['Y'][gen.pathYPos(pp['X'], pp['Y'], pp['Z'])] = True
        elif direction['Z'] != 0 : 
            gen.paths['Z'][gen.pathZPos(pp['X'], pp['Y'], pp['Z'])] = True

        gen.cube[ncp] = Generator.PIPE

        if self.cube[ncp] == Generator.STOP:
            return gen

        if self.cube[ncp] != Generator.EMPTY:
            return None

        return gen.buildPath(n)

    def fillHoles(self):

        pos = [ { 'X':x, 'Y':y, 'Z':z } 
            for x in range(self.sizeX) 
            for y in range(self.sizeY)
            for z in range(self.sizeZ) 
        ]
        random.shuffle(pos)

        while len(pos):
            p = pos.pop()
            if self.cube[self.cubePos(p['X'], p['Y'], p['Z'])] != Generator.EMPTY:
                continue
            self.fillHole(p)

    def fillHole(self, pos:dict):
        dirs = [
            { 'X':-1, 'Y':0, 'Z':0 },
            { 'X': 1, 'Y':0, 'Z':0 },
            { 'X':0, 'Y':-1, 'Z':0 },
            { 'X':0, 'Y': 1, 'Z':0 },
            { 'X':0, 'Y':0, 'Z':-1 },
            { 'X':0, 'Y':0, 'Z': 1 },
        ]
        random.shuffle(dirs)

        while len(dirs):
            d = dirs.pop()
            n = dict(pos)
            v = 0
            for k in n: 
                n[k] += d[k]
                v += d[k]

            if not self.isValidPosition(n):
                continue

            dst = self.cube[self.cubePos(n['X'], n['Y'], n['Z'])]
            if not dst in [Generator.EMPTY, Generator.PIPE]:
                continue

            self.cube[self.cubePos(pos['X'], pos['Y'], pos['Z'])] = Generator.PIPE

            if v > 0:
                pp = pos
            else:
                pp = n
            if d['X'] != 0 :
                if self.paths['X'][self.pathXPos(pp['X'], pp['Y'], pp['Z'])]: continue
                self.paths['X'][self.pathXPos(pp['X'], pp['Y'], pp['Z'])] = True
            elif d['Y'] != 0 : 
                if self.paths['Y'][self.pathYPos(pp['X'], pp['Y'], pp['Z'])]: continue
                self.paths['Y'][self.pathYPos(pp['X'], pp['Y'], pp['Z'])] = True
            elif d['Z'] != 0 : 
                if self.paths['Z'][self.pathZPos(pp['X'], pp['Y'], pp['Z'])]: continue
                self.paths['Z'][self.pathZPos(pp['X'], pp['Y'], pp['Z'])] = True

            return
