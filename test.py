import pygame
import os
import main as fpa
from typing import Final

pygame.init()

DIRECTORY=os.path.dirname(__file__)+"/"

container=fpa.Container(pygame.display.set_mode((800,600),pygame.RESIZABLE),DIRECTORY)

const_x=0
const_y=0
size_const=container.width/20

#testobj=fpa.GraphicalObject("nome",(lambda:0,lambda:10),(lambda:100,lambda:100))
#testobj2=fpa.GraphicalSprite("boh",pos_pointers=(lambda:x,lambda:0),size_pointers=(lambda:100,lambda:100))

def gridBuilder(xSize,ySize):
    for x in range(xSize):
        for y in range(ySize):
            fpa.GraphicalSprite("field"+str(x)+","+str(y),size_pointers=(lambda: size_const,lambda: size_const),pos_pointers=(lambda x=x: const_x+(x*size_const),lambda y=y: const_y+(y*size_const)))#Super cool: this is how to make references to variables which don't change in lambda functions' context.

gridBuilder(20,20)

#print(fpa.GraphicalBase.container.object_dict)

running=True

#Setting clock
clock=pygame.time.Clock()
FPS=60
updatesPerFrame=30
updateInFrame=FPS/updatesPerFrame#Stores how many frames it takes to have an update
frame=0

while running:
    #Game updates
    for event in pygame.event.get():
        print(event)#This is SUPER useful
        if event.type == pygame.QUIT:
            running=False
        elif event.type==pygame.TEXTINPUT:
            if event.text=="d":
                const_x+=10
            elif event.text=="a":
                const_x-=10
            elif event.text=="w":
                const_y-=10
            elif event.text=="s":
                const_y+=10
        elif event.type == pygame.VIDEORESIZE:
            container.resize(event.size[0],event.size[1])
            size_const=container.width/20
    container.screen.fill((0,144,255))

    container.draw()

    pygame.display.update()
    clock.tick(FPS)