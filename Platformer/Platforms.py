from Globals import *
import pygame


class Platform(pygame.sprite.Sprite):
    """ creates platforms """
    platformImage = pygame.image.load("png\\Platform.png");

    def __init__(self, pos, size=(100, 20), color='green'):
        pygame.sprite.Sprite.__init__(self, (Variables.staticBodies, Variables.allSprites))

        self.image = pygame.transform.scale(self.platformImage, (int(size[0]), int(size[1])))
        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.pos = pygame.Vector2(pos)
        self.rect.center = self.pos

    def update(self):
        """function updates position of platforms"""
        self.rect.center = self.pos + Variables.cameraPos
