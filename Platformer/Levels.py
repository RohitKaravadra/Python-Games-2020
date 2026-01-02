from Platforms import *
import json


class Levels:
    # Level = {'1': Background}
    LevelPlatforms = dict()
    LevelEnemies = dict()

    @classmethod
    def load_level(cls):
        file = open("Level.txt")
        data = file.readline()
        if len(data) > 2:
            cls.LevelPlatforms = json.loads(data)
            data = file.readline()
            if len(data) > 2:
                cls.LevelEnemies = json.loads(data)

        for i in cls.LevelPlatforms:
            for j in cls.LevelPlatforms[i]:
                Platform(j[0] + pygame.Vector2(800, 0) * (int(i) - 1), j[1])
