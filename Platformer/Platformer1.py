import pygame
import time
import json

pygame.init()

# Global variables
DisplayWidth = 800
DisplayHeight = 450
DelTime = 0
FPS = 60
AllSprites = pygame.sprite.Group()
StaticBodies = pygame.sprite.Group()
Particles = pygame.sprite.Group()
Joystick = 0
p = pygame.sprite.Sprite()

# initializing window
Display = pygame.display.set_mode((DisplayWidth, DisplayHeight))
pygame.display.set_caption("Main")


class UI(pygame.sprite.Sprite):
    class HealthBar(pygame.sprite.Sprite):
        def __init__(self, parent):
            pygame.sprite.Sprite.__init__(self)

            self.parent = parent
            self.image = pygame.Surface((self.parent.health, 5))
            self.image.fill('green')
            self.rect = self.image.get_rect()
            self.rect.center = (60, 10)
            self.Background(self)

            AllSprites.add(self)

        class Background(pygame.sprite.Sprite):
            def __init__(self, parent):
                pygame.sprite.Sprite.__init__(self)
                self.image = parent.image.copy()
                self.image.fill('red')
                self.rect = self.image.get_rect()
                self.rect.center = parent.rect.center

                AllSprites.add(self)

        def update(self):
            self.image = pygame.Surface((self.parent.health, 5))
            self.image.fill('green')


class Particle(pygame.sprite.Sprite):
    """ particle system contains all the particle effects"""

    class Tail(pygame.sprite.Sprite):
        """ creates a tail for any moving object """

        def __init__(self, parent, intensity=10, decay=20):
            pygame.sprite.Sprite.__init__(self)

            self.pos = tuple(parent.pos)

            self.image = parent.image.copy()
            self.rect = self.image.get_rect()
            self.rect.center = self.pos

            self.alpha = intensity
            self.alpha_loss = self.alpha * decay / 100

            Particles.add(self)

        def update(self):
            if self.alpha > 0:
                self.alpha -= self.alpha_loss * DelTime * FPS
                self.rect.center = self.pos
                self.image.set_alpha(self.alpha)
                return

            self.kill()


class Levels:
    current_level = '1'
    # Level = {'1': Background}
    LevelPlatforms = dict()
    LevelEnemies = dict()
    max_level = 0

    @classmethod
    def load_level_data(cls):
        file = open('Level.txt')
        data = file.readline()
        if len(data) > 2:
            cls.LevelPlatforms = json.loads(data)
            cls.LevelEnemies = json.loads(file.readline())
        cls.max_level = len(cls.LevelPlatforms)

    @classmethod
    def load_level(cls):
        for i in StaticBodies:
            i.kill()
        for i in Enemies.AllEnemies:
            i.kill()
        for i in cls.LevelPlatforms[cls.current_level]:
            Platforms(i[0], i[1])
        for i in cls.LevelEnemies[cls.current_level]:
            if i[0] in 'redbox':
                Enemies.RedBox(i[1], cls.current_level)
            if i[0] in 'Fly':
                Enemies.Fly(i[1], i[2], cls.current_level)


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
            self.rect = pygame.Rect((0, 0, parent.rect.width // 3, parent.rect.height // 2))
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


class Enemies(pygame.sprite.Sprite):
    """ contains properties of different enemies """
    AllEnemies = pygame.sprite.Group()

    @classmethod
    def Hit(cls, obj):
        if not p.invincible and obj.rect.colliderect(p.rect):
            p.health -= 25
            p.active_invincibility()

    class RedBox(pygame.sprite.Sprite):
        def __init__(self, spawn, level):
            pygame.sprite.Sprite.__init__(self)

            self.image = pygame.Surface((15, 15))
            self.image.fill('red')

            self.rect = self.image.get_rect()
            self.pos = spawn
            self.rect.center = self.pos
            self.damage = 10

            self.H_speed = 1
            self.H_direction = 1
            self.V_direction = 1
            self.V_speed = 0

            self.on_ground = False
            self.level = level
            self.my_ground = pygame.sprite.Sprite()

            self.ground_object = CollisionObjects.GroundObject(self)

            Enemies.AllEnemies.add(self)
            AllSprites.add(self)

        def update(self):
            Enemies.Hit(self)

            if self.on_ground:
                self.check_direction()
                self.pos += pygame.Vector2(self.H_speed * DelTime * FPS * self.H_direction, 0)

            else:
                if self.V_speed < 3:
                    self.V_speed += 0.2 * DelTime * FPS
                self.pos += pygame.Vector2(0, (self.V_speed ** 2) / 2)

                self.on_ground = self.check_on_ground()

            self.rect.center = self.pos
            self.ground_object.update()
            Particle.Tail(self, 5, 5)

        def check_on_ground(self):
            collision = pygame.sprite.spritecollideany(self.ground_object, StaticBodies)
            if collision:
                self.V_speed = 0
                self.rect.midbottom = (
                    self.rect.midbottom[0], collision.rect.midtop[1] - 1)
                self.pos = self.rect.center
                self.my_ground = collision
                return True
            return False

        def check_direction(self):
            if self.rect.bottomleft[0] < self.my_ground.rect.bottomleft[0] and self.H_direction == -1:
                self.H_direction = 1
            if self.rect.bottomright[0] > self.my_ground.rect.bottomright[0] and self.H_direction == 1:
                self.H_direction = -1

    class Fly(pygame.sprite.Sprite):
        def __init__(self, spawn, size, level):
            pygame.sprite.Sprite.__init__(self)

            self.image = pygame.Surface((15, 15))
            self.image.fill('red')

            self.rect = self.image.get_rect()
            self.spawn = pygame.Vector2(spawn)
            self.pos = spawn
            self.rect.center = self.pos
            self.damage = 20
            self.level = level

            self.H_direction = 1
            self.H_range = size[0] / 2

            self.V_direction = 1
            self.V_range = size[1] / 2

            self.H_speed, self.V_speed = self.set_speed(self.H_range, self.V_range)

            Enemies.AllEnemies.add(self)
            AllSprites.add(self)

        def update(self):
            Enemies.Hit(self)

            if self.spawn.x - self.pos[0] > self.H_range:
                self.H_direction = 1
            elif self.pos[0] - self.spawn.x > self.H_range:
                self.H_direction = -1

            if self.spawn.y - self.pos[1] > self.V_range:
                self.V_direction = 1
            elif self.pos[1] - self.spawn.y > self.V_range:
                self.V_direction = -1

            self.pos += pygame.Vector2(self.H_speed * self.H_direction,
                                       self.V_speed * self.V_direction) * DelTime * FPS
            self.rect.center = self.pos
            Particle.Tail(self, 5, 5)

        @classmethod
        def set_speed(cls, a, b):
            if a > b:
                return 1, 0.5
            else:
                return 0.5, 1


class Platforms(pygame.sprite.Sprite):
    """ creates platforms """

    def __init__(self, pos, size=(100, 20), color='grey'):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.rect.center = pos

        AllSprites.add(self)
        StaticBodies.add(self)


class Player(pygame.sprite.Sprite):
    """ class containing all player properties """

    def __init__(self, spawn=(0, 0)):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((14, 14))
        pygame.draw.circle(self.image, 'green', (7, 7), 7)
        self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect()
        self.pos = spawn
        self.rect.center = self.pos
        self.health = 100

        self.H_speed = 3
        self.H_direction = 0
        self.V_direction = 1
        self.V_speed = 0
        self.on_ground = False

        self.is_jumping = False
        self.sprint = False
        self.jump_height = 4
        self.double_jump = 2
        self.wall_jump = False

        self.invincible = False
        self.invincibility_time = 0
        UI.HealthBar(self)

        self.collision_objects = CollisionObjects(self)

        AllSprites.add(self)

    def update(self):
        """ main update function og the body """
        self.on_ground = self.ground_check()
        self.update_pos()
        self.collision_objects.update()
        self.check_level()

        if self.invincible:
            self.check_invincibility()
        else:
            if not self.image.get_alpha() == 255:
                self.image.set_alpha(255)

    def update_pos(self):
        """ update position of the body according to the input """

        temp = pygame.Vector2()
        key = pygame.key.get_pressed()

        if Joystick:
            axis = Joystick.get_axis(0)
        else:
            axis = 0

        if key[pygame.K_d] or axis > 0:
            self.H_direction = 1
        elif key[pygame.K_a] or axis < 0:
            self.H_direction = -1
        else:
            self.H_direction = 0

        if self.collision_check():
            temp.x = 0
        else:
            if self.sprint:
                temp.x = (1 / 2) * self.H_direction * (self.H_speed ** 2.5)
            else:
                temp.x = self.H_speed * self.H_direction

        if self.is_jumping:
            self.V_speed -= 0.2 * DelTime * FPS
            if self.V_speed < 0:
                self.cancel_jump()
        elif not self.on_ground:
            if self.V_speed < 6:
                self.V_speed += 0.2 * DelTime * FPS
        else:
            self.V_speed = 0
            self.double_jump = 2

        if self.V_speed:
            temp.y = (1 / 2) * self.V_direction * (self.V_speed ** 2)

        if temp.magnitude():
            self.pos += temp * DelTime * FPS
            self.rect.center = self.pos
            Particle.Tail(self, 10, 10)

    def ground_check(self):
        """ check head and leg collision with ground """
        collision = pygame.sprite.spritecollide(self.collision_objects.ground, StaticBodies, False)
        if collision:
            if self.V_direction < 0:
                self.cancel_jump()
                self.rect.midtop = (
                    self.rect.midtop[0], collision[0].rect.midbottom[1] + 1)
                self.pos = self.rect.center
                return False
            if not self.on_ground:
                self.rect.midbottom = (
                    self.rect.midbottom[0], collision[0].rect.midtop[1] - 1)
                self.pos = self.rect.center
            return True
        return False

    def collision_check(self):
        """ check left and right collisions with objects """
        collision = pygame.sprite.spritecollide(self.collision_objects.side, StaticBodies, False)
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

    def active_sprint(self):
        self.sprint = True

    def cancel_sprint(self):
        self.sprint = False

    def check_level(self):
        """ check and change level if needed """

        change = True
        if int(Levels.current_level) > 1 and self.pos[0] < 0:
            Levels.current_level = str(int(Levels.current_level) - 1)
            self.pos += (DisplayWidth - 1, 0)
        elif int(Levels.current_level) < Levels.max_level and self.pos[0] > DisplayWidth:
            Levels.current_level = str(int(Levels.current_level) + 1)
            self.pos -= (DisplayWidth - 1, 0)
        else:
            change = False

        if change:
            Levels.load_level()

    def active_invincibility(self):
        self.invincible = True
        self.invincibility_time = time.time()

    def check_invincibility(self):
        if time.time() - self.invincibility_time > 1:
            self.invincibility_time = 0
            self.invincible = False
        else:
            if self.image.get_alpha():
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)


# main loop function
def main():
    global DelTime, Joystick, p

    Levels.load_level_data()
    Levels.load_level()
    p = Player((20, 440))
    last_time = time.time()

    while True:
        # respawn player
        if not p.alive():
            if not Levels.current_level == '1':
                Levels.current_level = '1'
                Levels.load_level()
            p.__init__((20, 440))

        # check for joystick connection
        if not pygame.joystick.get_count() == 0:
            if not Joystick:
                Joystick = pygame.joystick.Joystick(0)
                Joystick.init()
        else:
            Joystick = 0

        # check input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    p.jump()

                if event.key == pygame.K_LSHIFT:
                    p.active_sprint()

                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                    pygame.mouse.set_visible(not pygame.mouse.get_visible())

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    p.cancel_sprint()

            if Joystick:
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        p.jump()

                    if event.button == 5:
                        p.active_sprint()

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 5:
                        p.cancel_sprint()

        # update and print all the objects and Particles
        AllSprites.update()
        Particles.update()
        Display.fill('black')
        Particles.draw(Display)
        AllSprites.draw(Display)
        pygame.display.flip()

        # kill player if out of the view
        if p.pos[1] > DisplayHeight or p.health < 1:
            p.kill()

        # calculate delta time
        DelTime = time.time() - last_time
        last_time = time.time()


main()
