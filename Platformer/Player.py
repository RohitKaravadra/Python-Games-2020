from Levels import *
import pygame


class CollisionObjects(pygame.sprite.Sprite):
    """ colliding parts of a body"""

    def __init__(self, parent):
        self.ground = self.GroundObject(parent)
        self.side = self.SideObject(parent)

    class GroundObject(pygame.sprite.Sprite):
        """ ground collide object"""

        def __init__(self, parent):
            pygame.sprite.Sprite.__init__(self)
            self.parent = parent
            self.rect = pygame.Rect((0, 0, parent.rect.width // 2, parent.rect.height // 3))
            self.rect.center = parent.rect.midbottom

        def update(self):
            if self.parent.V_direction < 0:
                self.rect.center = self.parent.rect.midtop
            else:
                self.rect.center = self.parent.rect.midbottom

    class SideObject(pygame.sprite.Sprite):
        """ side collide object"""

        def __init__(self, parent):
            pygame.sprite.Sprite.__init__(self)
            self.parent = parent
            self.rect = pygame.Rect((0, 0, parent.rect.width // 2.5, parent.rect.height // 2))
            self.rect.center = parent.rect.center

        def update(self):
            if self.parent.H_direction > 0:
                self.rect.center = self.parent.rect.midright
            elif self.parent.H_direction < 0:
                self.rect.center = self.parent.rect.midleft
            else:
                self.rect.center = self.parent.rect.center

    def update(self):
        self.ground.update()
        self.side.update()


scale = (70, 70)


class Player(pygame.sprite.Sprite):
    """ class containing all player properties """
    playerSprites = {
        "Run":
            [pygame.transform.scale(pygame.image.load("png//Dino Walk ({}).png".format(i + 1)), scale) for i in
             range(6)],
        "idle":
            [pygame.transform.scale(pygame.image.load("png//Dino Idle ({}).png".format(i + 1)), scale) for i in
             range(3)],
        "slide":
            [pygame.transform.scale(pygame.image.load("png//Dino Slide ({}).png".format(i + 1)), scale) for i in
             range(2)],
        "jump":
            [pygame.transform.scale(pygame.image.load("png//Dino Jump (2).png"), scale)],
        "shoot":
            [pygame.transform.scale(pygame.image.load("png//Dino Jump ({}).png".format(i + 1)), scale) for i in
             range(4)]
    }

    def __init__(self, spawn=(0, 0)):
        pygame.sprite.Sprite.__init__(self)

        self.image = self.playerSprites["idle"][0]

        self.currentSprite = 0
        self.animation = "idle"
        self.spriteFlip = False

        self.rect = pygame.Rect(0, 0, 35, 45)
        self.pos = pygame.Vector2(Variables.displayCenter)
        self.rect.center = self.pos
        self.health = 100

        self.H_speed = 2
        self.H_direction = 1
        self.V_direction = 1
        self.V_speed = 0
        self.on_ground = False
        self.shoot = False

        self.is_jumping = False
        self.slide = False
        self.slideDistance = 0
        self.jump_height = 4.5
        self.double_jump = 2
        self.wall_jump = False

        self.collision_objects = CollisionObjects(self)

    def update(self):
        """ main update function og the body """
        self.on_ground = self.ground_check()
        self.update_pos()
        self.collision_objects.update()

        self.currentSprite += 10 * Variables.deltaTime
        if self.currentSprite >= self.playerSprites[self.animation].__len__():
            if self.animation == "shoot":
                self.shoot = False
            self.currentSprite = 0
        self.image = pygame.transform.flip(self.playerSprites[self.animation][int(self.currentSprite)],
                                           self.spriteFlip, 0)

    def draw(self):
        Variables.Display.blit(self.image, self.rect.topleft - pygame.Vector2(
            (self.image.get_width() - self.rect.width) // 2, (self.image.get_height() - self.rect.height) // 2))

    def update_pos(self):
        """ update position of the body according to the input """

        # getting input
        temp = pygame.Vector2()
        key = pygame.key.get_pressed()

        if Variables.Joystick:
            axis = Variables.Joystick.get_axis(0)
        else:
            axis = 0

        if key[pygame.K_d] or axis > 0:
            self.H_direction = 1
            self.spriteFlip = False
        elif key[pygame.K_a] or axis < 0:
            self.H_direction = -1
            self.spriteFlip = True
        else:
            self.H_direction = 0

        # setting animation
        if not self.on_ground:
            if self.slide:
                if not self.animation == "slide":
                    self.animation = "slide"
                    self.currentSprite = 0
            elif not self.animation == "jump":
                self.animation = "jump"
                self.currentSprite = 0
        elif self.shoot:
            if not self.animation == "shoot":
                self.animation = "shoot"
                self.currentSprite = 0
        elif self.H_direction == 0:
            if not self.animation == "idle":
                self.animation = "idle"
                self.currentSprite = 0
        else:
            if self.slide:
                if not self.animation == "slide":
                    self.animation = "slide"
                    self.currentSprite = 0
            elif not self.animation == "Run":
                self.animation = "Run"
                self.currentSprite = 0

        # stopping movement if collision
        if self.collision_check():
            temp.x = 0
            if self.slide:
                self.slide = False
                self.slideDistance = 0
        else:
            if self.slide:
                temp.x = (1 / 2) * self.H_direction * (self.H_speed ** 3.5)
                self.slideDistance += 1 * Variables.fps * Variables.deltaTime
                if self.slideDistance >= 20:
                    self.slide = False
                    self.slideDistance = 0
            else:
                temp.x = self.H_speed * self.H_direction

        # jump height calculations
        if self.is_jumping:
            self.V_speed -= 0.2 * Variables.deltaTime * Variables.fps
            if self.V_speed < 0:
                self.cancel_jump()
        elif not self.on_ground:
            if self.V_speed < 4.5:
                self.V_speed += 0.2 * Variables.deltaTime * Variables.fps
        else:
            self.V_speed = 0
            self.double_jump = 2

        if self.V_speed:
            temp.y = (1 / 2) * self.V_direction * (self.V_speed ** 2)

        # updating position
        if temp.magnitude():

            temp *= Variables.deltaTime * Variables.fps

            if temp.x < 0 and self.pos.x > Variables.innerBox.midleft[0]:
                self.pos.x += temp.x
                temp.x = 0
            elif temp.x > 0 and self.pos.x < Variables.innerBox.midright[0]:
                self.pos.x += temp.x
                temp.x = 0
            if temp.y < 0 and self.pos.y > Variables.innerBox.midtop[1]:
                self.pos.y += temp.y
                temp.y = 0
            elif temp.y > 0 and self.pos.y < Variables.innerBox.midbottom[1]:
                self.pos.y += temp.y
                temp.y = 0

        drag = Variables.displayCenter - self.pos
        if drag.magnitude() > 2:
            drag.scale_to_length(1.5)
            drag *= Variables.deltaTime * Variables.fps
            self.pos += drag
        else:
            drag.update((0, 0))

        self.rect.center = self.pos
        Variables.set_outerdisplay(temp - drag)

    def ground_check(self):
        """ check head and leg collision with ground """
        collision = pygame.sprite.spritecollide(self.collision_objects.ground, Variables.staticBodies, False)
        if collision:
            if self.V_direction < 0:
                self.cancel_jump()
                self.rect.midtop = (
                    self.rect.midtop[0], collision[0].rect.midbottom[1] + 1)
                self.pos = pygame.Vector2(self.rect.center)
                return False
            if not self.on_ground:
                self.rect.midbottom = (
                    self.rect.midbottom[0], collision[0].rect.midtop[1] - 1)
                self.pos = pygame.Vector2(self.rect.center)
            return True
        return False

    def collision_check(self):
        """ check left and right collisions with objects """
        collision = pygame.sprite.spritecollide(self.collision_objects.side, Variables.staticBodies, False)
        if collision:
            self.wall_jump = True
            return True
        self.wall_jump = False
        return False

    def jump(self):
        """ initializes jump if on ground or double jumping as well as wall jump if on wall"""
        if (self.double_jump == 2 and not self.on_ground or not self.double_jump) and not self.wall_jump:
            return
        self.is_jumping = True
        self.on_ground = False
        self.V_speed = self.jump_height
        self.V_direction = -1
        if not self.wall_jump:
            self.double_jump -= 1
        self.collision_objects.update()

    def cancel_jump(self):
        """ cancels jump """
        self.V_direction = 1
        self.V_speed = 0
        self.is_jumping = False

    def on_slide(self):
        if not self.slide:
            self.slide = True

    def on_shoot(self):
        if not self.shoot and self.on_ground and self.H_direction == 0:
            self.shoot = True
