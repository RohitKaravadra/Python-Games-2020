import pygame
import time

pygame.init()


class Variables:
    """globally used common variables"""
    resolution = 1280
    displayWidth = resolution
    displayHeight = 9 * resolution // 16
    displayCenter = pygame.Vector2(displayWidth // 2, displayHeight // 2)

    Display = pygame.display.set_mode((displayWidth, displayHeight))

    fps = 120
    deltaTime = 0
    allSprites = pygame.sprite.Group()
    staticBodies = pygame.sprite.Group()

    Joystick = False

    cameraPos = pygame.Vector2(600, 0)
    innerBox = pygame.Rect(0, 0, displayCenter.x // 2, displayCenter.y // 2)
    innerBox.center = displayCenter

    player = None

    """setter methods"""

    @classmethod
    def set_deltatime(cls, last_time):
        cls.deltaTime = time.time() - last_time

    @classmethod
    def set_outerdisplay(cls, pos):
        if pos.magnitude():
            cls.cameraPos -= pos
            if cls.cameraPos.y < -500:
                cls.restart()

    @classmethod
    def set_joystick(cls, status):
        if status:
            cls.Joystick = pygame.joystick.Joystick(0)
        else:
            cls.Joystick = False

    @classmethod
    def restart(cls):
        cls.cameraPos.y = 0
        cls.cameraPos.x = 600
        cls.player.pos = pygame.Vector2(Variables.displayCenter)
