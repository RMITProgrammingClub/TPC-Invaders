import pygame


class Keymap:
    """Decouple control to single buttons, check all keys assigned to a control
    all at once
    e.g.
    ```python
    k = Keymap(
        {
            "left": [pygame.K_LEFT, pygame.K_a],
            "right": [pygame.K_RIGHT, pygame.K_d],
            "shoot": [pygame.K_SPACE],
        }
    )
    k.refresh_map() # populates and updates keymap (after pygame inits)
    k.left() # returns True if either left or a is pressed
    k.right() # returns True if either right or d is pressed
    k.shoot() # returns True if space is pressed
    ```"""

    def __init__(self, keymap):
        self.get_pressed = None

        def is_pressed_fac(keys):
            def is_pressed():
                for k in keys:
                    if self.get_pressed[k]:
                        return True
                return False

            return is_pressed

        for (name, keys) in keymap.items():
            setattr(self, name, is_pressed_fac(keys))

    def refresh_map(self):
        self.get_pressed = pygame.key.get_pressed()
