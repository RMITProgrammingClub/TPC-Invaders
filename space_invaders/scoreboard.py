import pygame

from shared import WIDTH

"""Edit text with the keyboard."""
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)


class TextRow(pygame.sprite.Sprite):
    """A row of text."""

    def __init__(self, text, x=20, y=20, rect_anchor="topleft"):
        super().__init__()
        self.text = text
        self.font = pygame.font.SysFont(None, 48)
        self.color = WHITE
        self.x = x
        self.y = y
        self.rect_anchor = rect_anchor
        self.update()

    def update(self):
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.size = self.image.get_size()
        setattr(self.rect, self.rect_anchor, (self.x, self.y))


class Scoreboard:
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        x = WIDTH / 2
        self.texts = [
            TextRow("NEW HIGH SCORE!", x=x, y=40, rect_anchor="center"),
            TextRow("", x=20, y=80),
            TextRow("Text 789", x=20, y=140),
        ]
        self.text = ""

    def load(self, group):
        for text in self.texts:
            group.add(text)

    def push_event(self, event):
        if event.type == event.type == pygame.KEYDOWN:
            uc = event.unicode
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif uc.isalnum() or uc == " ":
                self.text += uc.upper()
            print(self.text)


# read scores from db
# check score, if score is highscore, show new highscore page
#    add new highscore, sort highscores, remove nth onwards scores, save scores to db
# finally, show leaderboard, any key to continue
