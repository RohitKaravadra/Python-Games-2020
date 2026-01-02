from Player import *


def main_loop():
    Levels.load_level()
    Variables.player = Player()
    last_time = time.time()
    background = pygame.transform.scale(pygame.image.load("png\\Background.png"), (Variables.displayWidth, Variables.displayHeight))

    """Detect joystick at start"""
    if pygame.joystick.get_count() > 0:
        Variables.set_joystick(True)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    Variables.player.jump()

                if event.key == pygame.K_LSHIFT:
                    Variables.player.on_slide()

                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

            if Variables.Joystick:
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        Variables.player.jump()

                    if event.button == 5:
                        Variables.player.on_slide()

                    if event.button == 1:
                        Variables.player.on_shoot()

            """detect joystick events in middle of execution"""
            if event.type == pygame.JOYDEVICEADDED and not Variables.Joystick:
                Variables.set_joystick(True)

            if event.type == pygame.JOYDEVICEREMOVED and Variables.Joystick:
                Variables.set_joystick(False)

        # Variables.Display.fill(pygame.Color("black"))
        Variables.Display.blit(background, (0, 0))
        Variables.player.update()
        Variables.allSprites.update()
        Variables.allSprites.draw(Variables.Display)
        Variables.player.draw()
        # pygame.draw.rect(Variables.Display, pygame.Color('red'), p.rect, 2)
        pygame.display.update()

        Variables.set_deltatime(last_time)
        last_time = time.time()


main_loop()
