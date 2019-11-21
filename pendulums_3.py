#pygame template

import pygame
import sys
import time
import random
import math
import numpy as np
from numpy import sin, cos, arcsin

from pygame.locals import *

class Bob():
    
    def __init__(self, s, v, a, m, colour, rodLength):
        self.s = s
        self.v = v
        self.a = a
        self.m = float(m)
        self.col = colour
        self.rad = int(BASERADIUS * m**(1/2))
        self.rodLength = rodLength

    def update_measures(self, newAngle):
        newV = ((newAngle - self.s) * FREQ + self.v)/2
        newA = ((newV - self.v) * FREQ + self.a)/2

        self.s = newAngle
        self.v = newV #* 1.007 # to counteract error maybe?
        self.a = newA

    def draw_pos(self, surface, pos):
        pygame.draw.circle(surface, self.col, cc(pos), self.rad)

    def draw_rod(self, surface, pos1, pos2):
        pygame.draw.line(surface, self.col, cc(pos1), cc(pos2), 3)


def cc(coords):
    x = coords[0]
    y = coords[1]
    x += CENTRE[0]
    y = -y
    y += CENTRE[1]
    return (int(x),int(y))

def render(surface, bobs, top, trailList):

    for i in range(len(trailList)):
        color = bobs[i].col
        for k in range(len(trailList[i])-1):
            pygame.draw.line(surface, color, cc(trailList[i][k]), cc(trailList[i][k+1]), 1)
    
    positions = []
    
    for i,bob in enumerate(bobs):
        if i == 0:
            topPos = top
        else:
            topPos = newPos
        
        yChange = -bob.rodLength * cos(bob.s)
        xChange = bob.rodLength * sin(bob.s)
        newPos = (topPos[0] + xChange, topPos[1] + yChange)
        positions.append(newPos)

        bob.draw_rod(surface, topPos, newPos)

    
    pygame.draw.circle(surface, BLACK, cc(top), 10)
    for i,bob in enumerate(bobs):
        position = positions[i]
        bob.draw_pos(surface, position)

        trailList[i].append(position)
        if len(trailList[i]) > TRAILLENGTH:
            trailList[i].pop(0)

 

    return trailList

def one_frame(bobs):

    angles = [bob.s for bob in bobs]
    speeds = [bob.v for bob in bobs]
    accs = [bob.a for bob in bobs]

    oldAngles = [bob.s for bob in bobs]
    oldSpeeds = [bob.v for bob in bobs]
    oldAccs = [bob.a for bob in bobs]

    #print(angles, speeds, accs)

    masses = [bob.m for bob in bobs]
    lengths = [bob.rodLength for bob in bobs]

    
    newAngles = [bob.s + (bob.v)/FPS for bob in bobs]
    n = len(bobs)

    if n == 1:
        h = 0
        oldH = 1
        while h != oldH:
            oldH = h
            h = ((-G*sin(angles[0] + h) / lengths[0] / FREQ**2) + speeds[0]/FREQ)
            
        newAngles[0] = (angles[0] + h)
    else:
        steps = [0 for x in range(n)]

        newSteps = [0.1 for x in range(n)]

        it = 0
        done = False
        
        while (not done or it < 10) and it < 200:

            done = True
            for a in range(n):
                if newSteps[a] != steps[a]:
                    done = False

                #angles[a] = (steps[a]/2 + oldAngles[a])
                #speeds[a] = ((steps[a]) * FREQ + oldSpeeds[a])/2
                #accs[a] = ((speeds[a] - oldSpeeds[a]) * FREQ + oldAccs[a])/2
            
            for a in range(n):
                
                if a == 0:
                    part1 = lengths[0]* sum( sum(masses[i] for i in range(r, n)) * lengths[r]* (accs[r]*cos(angles[0] - angles[r]) - speeds[r]*sin(angles[0] - angles[r])*(speeds[0] - speeds[r])) for r in range(1, n))
                    divisor1 = lengths[0]**2 * sum( masses[i] for i in range(0, n))
                    part2 = lengths[0] * speeds[0] * sum( sum(masses[i] for i in range(r, n))*lengths[r]*speeds[r]*sin(angles[0] - angles[r]) for r in range(1, n))      +        sum(masses[i] for i in range(0, n)) * G * lengths[0] * sin(angles[0])

                    acc = (- part1 - part2 )/ divisor1
                    step = (acc / FREQ**2) + speeds[0]/ FREQ
                    newSteps[0] = step

                else:                                                                                                                                                       #
                    oneSum = sum(masses[i] for i in range(1, n)) * lengths[0] * (accs[0]*cos(angles[a] - angles[0]) - speeds[0]*sin(angles[a] - angles[0])*(speeds[a] - speeds[0]))
                    twoSum = sum (    (sum(masses[i] for i in range(r, n)) * lengths[r]* ( accs[r]*cos(angles[a] - angles[r]) - speeds[r]*sin(angles[a] - angles[r])*(speeds[a] - speeds[r])) ) for r in range(1, a))
                    threeSum = sum (    (sum(masses[i] for i in range(r, n)) * lengths[r]* ( accs[r]*cos(angles[a] - angles[r]) - speeds[r]*sin(angles[a] - angles[r])*(speeds[a] - speeds[r])) ) for r in range(a+1, n))
                    
                    part1 = lengths[a]* (oneSum + twoSum + threeSum)
                    divisor1 = lengths[a]**2 * sum( masses[i] for i in range(a, n))
                                                    #               #
                    fourSum = lengths[a]*speeds[a] * sum( masses[i] for i in range(1, n)) * (lengths[0]*speeds[0]*sin(angles[a]-angles[0]))
                    fiveSum = sum (lengths[r]*speeds[r]* sum(masses[i] for i in range(r, n))*sin(angles[a]-angles[r]) for r in range(1, a))
                    sixSum = sum (lengths[r]*speeds[r]* sum(masses[i] for i in range(r, n))*sin(angles[a]-angles[r]) for r in range(a+1, n))
                    sevenSum = sum(masses[k] for k in range(a, n)) * G * lengths[a] * sin(angles[a])
                    
                    part2 = fourSum + fiveSum + sixSum + sevenSum
                    #print(part1, part2, divisor1)
                    acc = (- part1 - part2 )/ divisor1
                    step = (acc / FREQ**2) + speeds[a]/ FREQ
                    newSteps[a] = step

                    #print(oneSum, twoSum, threeSum, fourSum, fiveSum, sixSum, sevenSum)
                    #input()

            steps = newSteps[:]
            it += 1

        for a in range(n):
            newAngles[a] = angles[a] + steps[a]

        
                        
        
    for i,bob in enumerate(bobs):
        bob.update_measures(newAngles[i])

    if n != 1:
        for n in range(len(bobs)):
            if steps[n] > 1:
                print(steps, it)
                return None

    return bobs

FPS = 60.0
FREQ = 10000.0
TRAILLENGTH = FPS*20
TOTALTIME = 25 # time of video in seconds
BASERADIUS = 5
FAILED = False

SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
CENTRE = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

G = 500

RED = (255,0,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
AQUA = (0,255,255)
BLUE = (0,0,255)
BLACK = (0,0,0)


if __name__ == '__main__':
    #pygame.key.set_repeat(FPS,FPS//3)

    bobNum = 2

    initialAngles = [random.random()*np.pi*2 - np.pi for a in range(bobNum)]
    initialSpeeds = [0 for a in range(bobNum)]
    lengths = [60 - 4*a for a in range(bobNum)]
    masses = [1 for a in range(bobNum)]
    colours = [RED, BLUE, GREEN] * 50

    #initialAngles = [2, 3]
    #lengths = [150, 130]
    initialAngles = [2, 1.8, 2.2, 2, 2.1, 2.3, 1.7, 1.7, 1.7, 1]

    print("Angles: ", initialAngles)
    print("Angular velocities: ", initialSpeeds)
    print("Lengths: ", lengths)
    print("Masses: ", masses)

    bobs = [Bob(initialAngles[a], initialSpeeds[a], 0, masses[a], colours[a], lengths[a]) for a in range(bobNum)]
    top = (0,0)
           
    angleList = [[] for a in range(len(bobs))]
    

    for x in range(int(TOTALTIME*FREQ)):
        if (x+1) % (FREQ//10) == 0:
            print((x+1),  '/',  int(TOTALTIME*FREQ), ' : ', 100*float(x+1) / int(TOTALTIME*FREQ), '%')

        if not FAILED:
            newBobs = one_frame(bobs)
            if newBobs == None:
                FAILED = True
                print(x)
                input()
            else:
                bobs = newBobs[:]
                for i, bob in enumerate(bobs):
                    angleList[i].append(bob.s)

    print(angleList[0][:10])
    input()

    pygame.init()
    fpsClock=pygame.time.Clock()

    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    surface.fill((255,255,255))
    clock = pygame.time.Clock()

    pygame.key.set_repeat(1, 40)

        
    screen.blit(surface, (0,0))
    
    
    while True:
        count = 0
        surface.fill((255,255,255))
        screen.blit(surface, (0,0))
        pygame.display.update()
        trailList = [[] for a in range(len(bobs))]
        print('playing')
        while count < TOTALTIME*FREQ:

            

            surface.fill((255,255,255))

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
                    if event.key == K_PERIOD:
                        pass

            #bobs = one_frame(bobs)

            for i, bob in enumerate(bobs):
                bob.s = angleList[i][count]
            
            trailList = render(surface, bobs, top, trailList)
            
            

            #puts the surface onto the screen
            screen.blit(surface, (0,0))

            pygame.display.flip()
            pygame.display.update()
            fpsClock.tick(FPS)
            count += int(FREQ/FPS)

        input('stopped: continue?')
