import pygame
import json

pygame.init()

win = pygame.display.set_mode((800, 600))

AllBodies = pygame.sprite.Group()

MousePosition = tuple()
Selected = None


class Levels:
    LevelPlatforms = dict()
    LevelEnemies = dict()

    @classmethod
    def load_current_levels(cls):
        file = open('Level.txt')
        data = file.readline()
        if len(data) > 2:
            cls.LevelPlatforms = json.loads(data)
            cls.LevelEnemies = json.loads(file.readline())

    @classmethod
    def delete_last_level(cls):
        last_level = str(len(cls.LevelPlatforms))
        if last_level == '0':
            print("No Level To Delete")
            return

        cls.LevelPlatforms.pop(last_level)
        try:
            cls.LevelEnemies.pop(last_level)
        except KeyError:
            pass
        cls.save_level_data()
        print("Level " + last_level + " Deleted")

    @classmethod
    def save_level_data(cls):
        file = open('level.txt', 'w')
        data = json.dumps(cls.LevelPlatforms)
        data += "\n" + json.dumps(cls.LevelEnemies)
        file.write(data)


def text_surface(text, size=50, color='red', background='yellow'):
    font = pygame.font.SysFont("Times New Roman", size)
    text_rect = font.render(text, True, color, background)
    return text_rect


def save():
    level = list()
    enemies = list()

    for i in Platforms.AllPlatforms:
        level.append([tuple(i.rect.center), tuple(i.size)])
    for i in Enemies.AllEnemies:
        if 'redbox' in i.type:
            enemies.append([i.type, tuple(i.rect.center)])
        elif 'Fly' in i.type:
            enemies.append([i.type, tuple(i.rect.center), tuple(i.size)])

    number = str(len(Levels.LevelPlatforms) + 1)
    Levels.LevelPlatforms.update({number: level})
    Levels.LevelEnemies.update({number: enemies})
    Levels.save_level_data()
    print("Level {} Added".format(len(Levels.LevelPlatforms)))


class Buttons(pygame.sprite.Sprite):
    AllButtons = pygame.sprite.Group()

    def __init__(self, pos, text='text'):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.image = text_surface(text=text, color='red', background='green')
        self.image = pygame.transform.scale(self.image, (100, 20))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.type = text

        self.AllButtons.add(self)

    def update(self):
        self.on_press()

    def on_press(self):
        if 'platform' in self.type:
            Platforms()
        if 'Add Level' in self.type:
            save()
        if 'redbox' in self.type:
            Enemies('redbox')
        if 'Fly' in self.type:
            Enemies('Fly')


class Enemies(pygame.sprite.Sprite):
    """ creates platforms """
    AllEnemies = pygame.sprite.Group()

    def __init__(self, type):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((15, 15))
        if 'Fly' in type:
            self.color = 'orange'
        else:
            self.color = 'red'
        self.image.fill(self.color)
        self.image.set_alpha(50)
        self.rect = self.image.get_rect()
        self.rect.center = (10, 10)
        self.type = type
        self.size = self.image.get_size()

        self.AllEnemies.add(self)
        AllBodies.add(self)

    def update(self):
        if 'redbox' in self.type:
            if 0 < MousePosition[0] < 800 and 0 < MousePosition[1] < 450:
                self.rect.center = MousePosition

        if 'Fly' in self.type:
            if 0 < MousePosition[0] < 800 and 0 < MousePosition[1] < 450:
                key = pygame.key.get_pressed()

                change = pygame.Vector2(0, 0)
                if key[pygame.K_UP] or key[pygame.K_w]:
                    change.y += 1
                if (key[pygame.K_DOWN] or key[pygame.K_s]) and self.size[1] > 1:
                    change.y -= 1
                if key[pygame.K_RIGHT] or key[pygame.K_d]:
                    change.x += 1
                if (key[pygame.K_LEFT] or key[pygame.K_a]) and self.size[0] > 1:
                    change.x -= 1

                if change.magnitude():
                    self.size += change * 0.5
                    self.image = pygame.Surface(self.size)
                    self.image.fill(self.color)
                    self.image.set_alpha(50)
                    self.rect = self.image.get_rect()

                self.rect.center = MousePosition


class Platforms(pygame.sprite.Sprite):
    """ creates platforms """
    AllPlatforms = pygame.sprite.Group()

    def __init__(self, pos=(10, 10), size=(50, 50), color='green'):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.image.set_alpha(50)
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.size = size

        self.AllPlatforms.add(self)
        AllBodies.add(self)

    def update(self):
        if 0 < MousePosition[0] < 800 and 0 < MousePosition[1] < 450:
            key = pygame.key.get_pressed()

            change = pygame.Vector2(0, 0)
            if key[pygame.K_UP] or key[pygame.K_w]:
                change.y += 1
            if (key[pygame.K_DOWN] or key[pygame.K_s]) and self.size[1] > 1:
                change.y -= 1
            if key[pygame.K_RIGHT] or key[pygame.K_d]:
                change.x += 1
            if (key[pygame.K_LEFT] or key[pygame.K_a]) and self.size[0] > 1:
                change.x -= 1

            if change.magnitude():
                self.size += change * 0.5
                self.image = pygame.Surface(self.size)
                self.image.fill(self.color)
                self.image.set_alpha(50)
                self.rect = self.image.get_rect()

            self.rect.center = MousePosition


Buttons((5, 500), 'platform')
Buttons((120, 500), 'redbox')
Buttons((235, 500), 'Fly')
Buttons((5, 550), ' Add Level ')

Levels.load_current_levels()


def mainloop():
    while True:
        global MousePosition, Selected, Levels
        pygame.time.Clock().tick_busy_loop(90)

        MousePosition = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_DELETE:
                    Levels.delete_last_level()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in Buttons.AllButtons:
                        if i.rect.collidepoint(MousePosition):
                            i.on_press()
                            break
                    else:
                        if Selected:
                            Selected = None
                        else:
                            for i in AllBodies:
                                if i.rect.collidepoint(MousePosition):
                                    Selected = i
                                    break

                if event.button == 3 and Selected:
                    Selected.kill()
                    Selected = None

        # win.blit(Background, (0, 0))
        win.fill('black')
        pygame.draw.rect(win, pygame.Color('yellow'), (0, 0, 800, 450), 2)
        if Selected:
            Selected.update()
        Buttons.AllButtons.draw(win)
        AllBodies.draw(win)
        if Selected:
            pygame.draw.rect(win, 'cyan', Selected.rect, 1)
        pygame.display.flip()


mainloop()
