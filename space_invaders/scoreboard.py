import pygame

from shared import WIDTH

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)


class TextRow(pygame.sprite.Sprite):
    """A row of text."""

    def __init__(self, text, x=20, y=20, rect_anchor="topleft", size=48):
        pygame.sprite.Sprite.__init__(self)
        self.text = text
        self.font = pygame.font.SysFont(None, size)
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


def odnl(n):
    return "%d%s" % (n, "tsnrhtdd"[(n//10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def load_scores():
    """Load the scores from the scores.txt file."""

    def name_score(line):
        return [line.split(",")[0], int(line.split(",")[1])]

    with open("scores.txt", "r") as f:
        scores = [name_score(line) for line in f.read().splitlines()]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def save_score(scores):
    """Save the scores to the scores.txt file."""
    with open("scores.txt", "w") as f:
        for name, score in scores:
            f.write(f"{name},{score}\n")


class Scoreboard:
    def __init__(self):
        self.scores = load_scores()
        pygame.sprite.Sprite.__init__(self)
        self.texts = []
        self.text = ""
        self.adding_new_score = False

    def paint_new_score_screen(self, score):
        self.adding_new_score = score
        x = WIDTH / 2
        self.input_text = TextRow(self.text, x=x, y=120, rect_anchor="center")
        self.texts = [
            TextRow("NEW HIGH SCORE!", x=x, y=40, rect_anchor="center"),
            TextRow(str(score), x=x, y=80, rect_anchor="center"),
            self.input_text,
            TextRow("Enter Your Initials", x=x, y=160, size=20, rect_anchor="center",),
        ]

    def paint_highscores_screen(self):
        self.clear_texts()

        x = WIDTH / 2

        def text_row(text, offset):
            return TextRow(text, x=x, y=offset, rect_anchor="center")
        self.texts.append(text_row("HIGH SCORES", 50))
        self.texts.append(text_row("{:5}{:10}{:5}".format("RANK", "NAME", "SCORE"), 100))
        for i, (name, score) in enumerate(self.scores):
            rank = odnl(i + 1)
            t = f"{rank:5} {name:10} {score:5}"
            self.texts.append(text_row(t, 150 + i * 50))
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"high_scores_text": True}))

    def apply_score(self):
        self.scores.append([self.text, self.adding_new_score])
        self.scores.sort(key=lambda x: x[1], reverse=True)
        self.scores = self.scores[:10]
        save_score(self.scores)
        self.adding_new_score = False

    def new_score(self, score):
        if len(self.scores) < 10 or score > self.scores[:-1][1]:
            self.paint_new_score_screen(score)
        else:
            self.paint_highscores_screen()

    def load(self, group):
        for text in self.texts:
            group.add(text)

    def clear_texts(self):
        for text in self.texts:
            text.kill()
        self.texts = []

    def accept_event(self, event):
        if event.type == pygame.KEYDOWN:
            uc = event.unicode
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            if event.key == pygame.K_RETURN:
                if self.adding_new_score:
                    self.apply_score()
                    self.paint_highscores_screen()
                else:
                    pygame.event.post(
                        pygame.event.Event(pygame.USEREVENT, {"on_reset": True})
                    )
            elif uc.isalnum() | uc in " -!?$:<>.":
                self.text += uc.upper()[:10]
            self.update()

    def update(self):
        if self.adding_new_score:
            self.input_text.text = self.text
            self.input_text.update()
        for text in self.texts:
            text.update()


# read scores from db
# check score, if score is highscore, show new highscore page
#    add new highscore, sort highscores, remove nth onwards scores, save scores to db
# finally, show leaderboard, any key to continue
