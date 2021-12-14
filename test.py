import pygame
import os
import main as fpa

pygame.init()

DIRECTORY=os.path.dirname(__file__)+"/"

container=fpa.Container(pygame.display.set_mode((800,600),pygame.RESIZABLE),DIRECTORY)

testobj=fpa.GraphicalObject("nome",(lambda:0,lambda:10),(lambda:100,lambda:100))
testobj2=fpa.GraphicalSprite("boh",pos_pointers=(lambda:0,lambda:10),size_pointers=(lambda:1000,lambda:100))

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
    container.screen.fill((0,144,255))

    container.draw()

    pygame.display.update()
    clock.tick(FPS)