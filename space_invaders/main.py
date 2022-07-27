import random
import pygame
from pygame.event import Event as PgEvent
import time

from keymap import Keymap
from scoreboard import Scoreboard, TextRow
from shared import HEIGHT, WIDTH


SCALE = 1
SCALE_WIDTH, SCALE_HEIGHT = WIDTH * SCALE, HEIGHT * SCALE
FPS = 60

pygame.init()
pygame.mixer.init()

# Sprite Collision Groups
bullet_group = pygame.sprite.Group()
alien_bullet_group = pygame.sprite.Group()
alien_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()

keymap = Keymap(
    {
        "left": [pygame.K_LEFT, pygame.K_a],
        "right": [pygame.K_RIGHT, pygame.K_d],
        "up": [pygame.K_UP, pygame.K_w],
        "down": [pygame.K_DOWN, pygame.K_s],
        "shoot": [pygame.K_SPACE],
    }
)


# create spaceship class
class Spaceship(pygame.sprite.Sprite):
    SHOOT_SOUND = pygame.mixer.Sound("sounds/laser_shot.wav")
    COOL_DOWN = 333

    def __init__(self, x, y, health, go_cb):
        pygame.sprite.Sprite.__init__(self)
        self.load_sprites()
        self.image = self.player_sprite_n
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.last_shot = pygame.time.get_ticks()
        self.go_cb = go_cb

        # Shooting Sound

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
        dx = 0
        dy = 0

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

        if keymap.up() and self.rect.top > 0:
            dy = -1
        elif keymap.down() and self.rect.bottom < HEIGHT:
            dy = 1
        else:
            dy = 0

        # On Space press create bullet at position
        if keymap.shoot() and time_now - self.last_shot > Spaceship.COOL_DOWN:
            # Add Bullet to sprite group
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullet_group.add(bullet)

            # Play laser shot sound
            Spaceship.SHOOT_SOUND.play()
            self.last_shot = time_now

        # Move the ship
        self.rect.x += dx * speed * dt
        self.rect.y += dy * speed * dt

        col = pygame.sprite.spritecollide(self, alien_bullet_group, True)
        if len(col) > 0:
            for bullet in col:
                bullet.kill()
            self.kill()
            self.go_cb()


class Alien(pygame.sprite.Sprite):
    SOUND = pygame.mixer.Sound("sounds/alien_shot.wav")
    DIRECTION = ""
    BULLET_CHANCE = 0
    SPEED = 0
    MOV_INC = 0
    MOV_TIMER = 0
    OFFSET_X = 0
    OFFSET_Y = 0

    def reset():
        Alien.DIRECTION = "right"
        Alien.BULLET_CHANCE = 0.01
        Alien.SPEED = 10
        Alien.MOV_INC = 2000
        Alien.MOV_TIMER = 0
        Alien.OFFSET_X = 0
        Alien.OFFSET_Y = 0

    def __init__(self, x, y, dir=1):
        pygame.sprite.Sprite.__init__(self)
        self.load_sprite()
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.timer = 0
        self.mov_timer = 0
        self.x = x
        self.y = y

    def load_sprite(self):
        self.image_sheet = pygame.image.load(
            "sprites/Alan (16 x 16).png"
        ).convert_alpha()
        self.sprites = []
        self.sprites.append(self.image_sheet.subsurface((48, 0, 16, 16)))
        self.sprites.append(self.image_sheet.subsurface((64, 0, 16, 16)))
        self.sprites.append(self.image_sheet.subsurface((80, 0, 16, 16)))

        for i in range(len(self.sprites)):
            self.sprites[i] = pygame.transform.scale(self.sprites[i], (32, 32))

        self.image = self.sprites[0]
        self.image_index = 0

    def update(self, dt, time_now):
        if self.rect.left - Alien.SPEED < 0 and Alien.DIRECTION != "right":
            Alien.DIRECTION = "right"
            Alien.OFFSET_Y += Alien.SPEED
        elif self.rect.right + Alien.SPEED > WIDTH and Alien.DIRECTION != "left":
            Alien.DIRECTION = "left"
            Alien.OFFSET_Y += Alien.SPEED
        if time_now - Alien.MOV_TIMER >= Alien.MOV_INC:
            if Alien.DIRECTION == "right":
                Alien.OFFSET_X += Alien.SPEED
            else:
                Alien.OFFSET_X -= Alien.SPEED
            Alien.MOV_TIMER = time_now
        self.rect.x = self.x + Alien.OFFSET_X
        self.rect.y = self.y + Alien.OFFSET_Y
        if self.rect.bottom > HEIGHT:
            pygame.event.post(PgEvent(pygame.USEREVENT, {"game_over": True}))
        if time_now - self.timer >= 300:
            self.image_index += 1
            if self.image_index >= len(self.sprites):
                self.image_index = 0
            # print("SPRITE CAHNGE")
            if not App.GAME_OVER and random.random() < Alien.BULLET_CHANCE:
                alien_bullet_group.add(
                    Alien_Bullet(self.rect.centerx, self.rect.bottom)
                )
                Alien.SOUND.play()
            self.image = self.sprites[self.image_index]
            self.timer = time_now


Alien.reset()


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
            pygame.event.post(PgEvent(pygame.USEREVENT, {"add_score": 1}))


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
        alien_group.empty()
        for row in range(rows):
            for item in range(cols):
                alien = Alien(80 + item * 64, 100 + row * 64)
                alien_group.add(alien)
        return alien_group

    def create_surface(self, a, b):
        self.surface = pygame.Surface((WIDTH, HEIGHT))
        for y in range(int(HEIGHT / 64) + 64):
            for x in range(int(WIDTH / 64) + 64):
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

    LEVEL_UP_SOUND = pygame.mixer.Sound("sounds/alien_sound.mp3")
    GAME_START_SOUND = pygame.mixer.Sound("sounds/game_start_sound.wav")

    # Initialize varibles for Application Class
    def __init__(self):
        # Clock for FPS limiting
        self.clock = pygame.time.Clock()
        # Time for delta time
        self.dt = 0
        self.prev_time = time.time()
        App.GAME_OVER = False
        # Pygame varibles
        self.running = True
        self._display_surf = None
        self.size = self.weight, self.height = SCALE_WIDTH, SCALE_HEIGHT
        self.score = 0

    def on_init(self):
        # Pygame Surface initialisation
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE)
        self._running = True

        self.level = Level(self.on_game_over)

        # Initialise groups
        self.spaceship = Spaceship(int(WIDTH / 2), HEIGHT - 50, 3, self.on_game_over)

        self.scoreboard = Scoreboard()

        self.player_group = player_group
        self.player_group.add(self.spaceship)

        self.score = 0
        self.score_text = TextRow("SCORE: 0", x=20, y=20, size=27)
        self.player_group.add(self.score_text)
        self.player_level = 0
        self.level_text = TextRow("LEVEL 0", x=20, y=60, size=27)
        self.player_group.add(self.level_text)

        self.bullet_group = bullet_group
        self.alien_group = alien_group
        self.alien_bullet_group = alien_bullet_group

        self.alien_group = self.level.create_aliens(5, 5, self.alien_group)

        # get rid of auto repeating keys
        pygame.key.set_repeat()

        App.GAME_START_SOUND.play()

    # Handle events
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.USEREVENT:
            if hasattr(event, "on_reset"):
                self.on_reset()
            elif hasattr(event, "add_score"):
                self.score += event.add_score
                self.score_text.text = f"SCORE: {str(self.score)}"
                self.score_text.update()
            elif hasattr(event, "high_scores_text"):
                self.scoreboard.load(self.player_group)
            elif hasattr(event, "game_over"):
                self.on_game_over()
            elif hasattr(event, "level_up"):
                if not App.GAME_OVER:
                    self.level_up()
        elif App.GAME_OVER:
            self.scoreboard.accept_event(event)

    def on_loop(self):
        self.clock.tick(FPS)
        self.now = time.time()
        self.dt = self.now - self.prev_time
        self.prev_time = self.now
        time_now = pygame.time.get_ticks()

        #  GAME LOGIC GOES HERE
        self.level.on_loop(time_now)
        if not App.GAME_OVER:
            self.spaceship.update(self.dt, time_now)
            self.alien_group.update(self.dt, time_now)
            if len(alien_group) == 0:
                pygame.event.post(PgEvent(pygame.USEREVENT, {"level_up": True}))

        self.bullet_group.update(self.dt, time_now)
        self.alien_group.update(self.dt, time_now)
        self.alien_bullet_group.update(self.dt, time_now)

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
        App.GAME_OVER = False
        self.on_init()
        Alien.reset()

    def level_up(self):
        App.LEVEL_UP_SOUND.play()
        Alien.OFFSET_X = 0
        Alien.OFFSET_Y = 0
        Spaceship.COOL_DOWN = 333 ** (1 - self.player_level / 10)
        self.level.create_aliens(6, 6, self.alien_group)
        self.player_level += 1
        Alien.MOV_INC = 1800 ** (1 - self.player_level / 10)
        self.level_text.text = f"LEVEL {self.player_level}"
        self.level_text.update()

    def on_game_over(self):
        App.GAME_OVER = True
        pygame.key.set_repeat(400, 100)
        self.alien_group.empty()
        self.score_text.kill()
        self.level_text.kill()
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
