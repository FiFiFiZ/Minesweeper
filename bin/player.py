import pygame
from math import*
from random import*
from assets import Assets

class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self.assets = Assets()


    def main(self):
        # print(self.grid)
        pass