import random
import pygame
import time

from keymap import Keymap
from scoreboard import Scoreboard, TextRow
from shared import HEIGHT, WIDTH


SCALE = 1
SCALE_WIDTH, SCALE_HEIGHT = WIDTH * SCALE, HEIGHT * SCALE
FPS = 60

# Game Over Flag
GAME_OVER = False


# Sprite Collision Groups
bullet_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

keymap = Keymap(
    {
        "left": [pygame.K_LEFT, pygame.K_a],
        "right": [pygame.K_RIGHT, pygame.K_d],
        "shoot": [pygame.K_SPACE],
    }
)


# create spaceship class
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y, health, go_cb):
        pygame.sprite.Sprite.__init__(self)
        self.load_sprites()
        self.image = self.player_sprite_n
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.last_shot = pygame.time.get_ticks()
        self.go_cb = go_cb

        # Shooting Sound
        self.shoot_sound = pygame.mixer.Sound("sounds/laser_shot.wav")

    def load_sprites(self):
        # Load the sprite sheet
        self.sprites = pygame.image.load(
            "sprites/Player_ship (16 x 16).png"
        ).convert_alpha()
        # Get the individual sprites
        self.player_sprite_n = self.sprites.subsurface((16, 0, 16, 16))
        self.player_sprite_r = self.sprites.subsurface((32, 0, 16, 16))
        self.player_sprite_l = self.sprites.subsurface((0, 0, 16, 16))
        # scale the sprites
        self.player_sprite_n = pygame.transform.scale(self.player_sprite_n, (32, 32))
        self.player_sprite_r = pygame.transform.scale(self.player_sprite_r, (32, 32))
        self.player_sprite_l = pygame.transform.scale(self.player_sprite_l, (32, 32))

    # Call every game update
    def update(self, dt, time_now):
        # set movement speed
        speed = 250
        # set a cooldown variable
        cooldown = 500  # milliseconds
        dx = 0

        # get key press for movement
        if keymap.left() and self.rect.left > 0:
            dx = -1  # Set the direction delta
            self.image = self.player_sprite_l  # Set the Sprite
        elif keymap.right() and self.rect.right < WIDTH:
            dx = 1  # Set the direction delta
            self.image = self.player_sprite_r  # Set the Sprite
        else:
            dx = 0  # Set the direction delta
            self.image = self.player_sprite_n  # Set the Sprite

        # On Space press create bullet at position
        if keymap.shoot() and time_now - self.last_shot > cooldown:
            # Add Bullet to sprite group
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)

            # Play laser shot sound
            self.shoot_sound.play()
            self.last_shot = time_now

        # Move the ship
        self.rect.x += dx * speed * dt

        col = pygame.sprite.spritecollide(self, alien_bullet_group, True)
        if len(col) > 0:
            for bullet in col:
                bullet.kill()
            self.kill()
            self.go_cb()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, dir=1, speed=5):
        pygame.sprite.Sprite.__init__(self)
        self.load_sprite()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = speed
        self.dir = dir
        self.timer = 0
        self.sound = pygame.mixer.Sound("sounds/alien_shot.wav")

    def load_sprite(self):
        self.image_sheet = pygame.image.load(
            "sprites/Alan (16 x 16).png"
        ).convert_alpha()
        self.dir = 1
        self.sprites = []
        self.sprites.append(self.image_sheet.subsurface((48, 0, 16, 16)))
        self.sprites.append(self.image_sheet.subsurface((64, 0, 16, 16)))
        self.sprites.append(self.image_sheet.subsurface((80, 0, 16, 16)))

        for i in range(len(self.sprites)):
            self.sprites[i] = pygame.transform.scale(self.sprites[i], (32, 32))

        self.image = self.sprites[0]
        self.image_index = 0

    def update(self, dt, time_now):

        if time_now - self.timer >= 300:
            self.image_index += 1
            if self.image_index >= len(self.sprites):
                self.image_index = 0
            # print("SPRITE CAHNGE")
            if not GAME_OVER and random.random() < 0.025:
                alien_bullet_group.add(
                    Alien_Bullet(self.rect.centerx, self.rect.bottom)
                )
                self.sound.play()
            self.image = self.sprites[self.image_index]
            self.timer = time_now


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            "sprites/Player_beam (16 x 16).png"
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = 500

    def update(self, dt, time_now):
        self.rect.y -= self.speed * dt

        if self.rect.y <= -5:
            self.kill()
        if pygame.sprite.spritecollide(self, alien_group, True):
            self.kill()
            print("HIT")
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"add_score": 1}))


class Alien_Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.load_sprite()
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.speed = 500

    def load_sprite(self):
        sprite_sheet = pygame.image.load(
            "sprites/Enemy_projectile (16 x 16).png"
        ).convert_alpha()
        self.image = sprite_sheet

    def update(self, dt, time_now):
        self.rect.y += self.speed * dt

        if self.rect.y >= HEIGHT:
            self.kill()


class Level:
    def __init__(self, game_over_cb):
        self.background = pygame.image.load(
            "sprites/Space_BG (2 frames) (64 x 64).png"
        ).convert_alpha()
        background_a = self.background.subsurface((0, 0, 64, 64))
        background_b = self.background.subsurface((64, 0, 64, 64))
        self.background_a = self.create_surface(background_a, background_b)
        self.background_b = self.create_surface(background_b, background_a)
        self.timer = 0
        self.game_over_cb = game_over_cb

    def create_aliens(self, rows, cols, alien_group):
        for row in range(rows):
            for item in range(cols):
                alien = Alien(80 + item * 64, 100 + row * 64)
                alien_group.add(alien)
        return alien_group

    def create_surface(self, a, b):
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        for y in range(0, int(HEIGHT / 64) + 64):
            for x in range(0, int(WIDTH / 64) + 64):
                if x * y % 2 == 0:
                    self.surface.blit(
                        pygame.transform.rotate(a, 90 * x), (x * 64, y * 64)
                    )
                else:
                    self.surface.blit(
                        pygame.transform.rotate(b, 90 * x), (x * 64, y * 64)
                    )

        self.surface.blit(self.background, (0, 0))
        return self.surface

    def get_surface(self):
        return (self.background_a, (0, 0))

    def on_loop(self, time_now):
        # print(time_now - self.timer)
        if time_now - self.timer > 1500:
            self.timer = time_now
            self.background_a, self.background_b = self.background_b, self.background_a


# Main Application class
class App:

    # Initialize varibles for Application Class
    def __init__(self):
        # Clock for FPS limiting
        self.clock = pygame.time.Clock()
        # Time for delta time
        self.dt = 0
        self.prev_time = time.time()
        global GAME_OVER
        GAME_OVER = False
        # Pygame varibles
        self.running = True
        self._display_surf = None
        self.size = self.weight, self.height = SCALE_WIDTH, SCALE_HEIGHT
        self.score = 0

    def on_init(self):
        # Pygame Surface initialisation
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE)
        self._running = True

        self.level = Level(self.on_game_over)

        # Initialise groups
        self.spaceship = Spaceship(int(WIDTH / 2), HEIGHT - 100, 3, self.on_game_over)

        self.scoreboard = Scoreboard()

        self.player_group = player_group
        self.player_group.add(self.spaceship)

        self.score = 0
        self.score_text = TextRow("SCORE: 0", x=20, y=20, size=20)
        self.player_group.add(self.score_text)

        self.bullet_group = bullet_group
        self.alien_group = alien_group
        self.alien_bullet_group = alien_bullet_group

        self.alien_group = self.level.create_aliens(6, 6, self.alien_group)

        # get rid of auto repeating keys
        pygame.key.set_repeat()

    # Handle events
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.USEREVENT:
            if hasattr(event, "on_reset"):
                self.on_reset()
            elif hasattr(event, "add_score"):
                self.score += event.add_score
                self.score_text.text = "SCORE: " + str(self.score)
                self.score_text.update()
            elif hasattr(event, "high_scores_text"):
                self.scoreboard.load(self.player_group)
        elif GAME_OVER:
            self.scoreboard.accept_event(event)

    def on_loop(self):
        global GAME_OVER
        self.clock.tick(FPS)
        self.now = time.time()
        self.dt = self.now - self.prev_time
        self.prev_time = self.now
        time_now = pygame.time.get_ticks()

        #  GAME LOGIC GOES HERE
        self.level.on_loop(time_now)
        if not GAME_OVER:
            self.spaceship.update(self.dt, time_now)

        self.bullet_group.update(self.dt, time_now)
        self.alien_group.update(self.dt, time_now)
        self.alien_bullet_group.update(self.dt, time_now)

        if len(alien_group) == 0:
            GAME_OVER = True

    # blit render layers to screen surface
    def on_render(self):
        temp_buffer = pygame.Surface((WIDTH, HEIGHT))
        temp_buffer.blit(*self.level.get_surface())

        self.alien_group.draw(temp_buffer)
        self.player_group.draw(temp_buffer)
        self.bullet_group.draw(temp_buffer)
        self.alien_bullet_group.draw(temp_buffer)
        temp_buffer = pygame.transform.scale(temp_buffer, (SCALE_WIDTH, SCALE_HEIGHT))
        self._display_surf.blit(temp_buffer, (0, 0))
        # update display
        pygame.display.update()

    def on_reset(self):
        self.bullet_group.empty()
        self.alien_bullet_group.empty()
        self.player_group.empty()
        self.alien_group.empty()
        global GAME_OVER
        GAME_OVER = False
        self.on_init()

    def on_game_over(self):
        global GAME_OVER
        GAME_OVER = True
        pygame.key.set_repeat(400, 100)
        self.alien_group.empty()
        self.scoreboard.new_score(self.score)
        self.scoreboard.load(self.player_group)

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if self.on_init() is False:
            self._running = False
        self.music = pygame.mixer.Sound("sounds/music.wav")
        self.music.play()

        while self._running:
            keymap.refresh_map()
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    app = App()
    app.on_execute()
