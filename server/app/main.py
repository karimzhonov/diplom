import os
import sys
import pygame

from main.models import Lock
from main.multi_socket import MultiSocket


class App:
    def __init__(self, title: str = 'Camera surveillance', display_shape=(1000, 600), frame_shape=(200, 150),
                 background_color=(0, 0, 0), color=(255, 255, 255)):
        self.dwidth, self.dheight = display_shape
        self.fwidth, self.fheight = frame_shape
        self.background_color = background_color
        self.color = color
        self.col_count = int(self.dwidth / self.fwidth)
        self.row_count = int(self.dheight / self.fheight)

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(title)
        self.font = pygame.font.SysFont('arial', 14)
        self.screen = pygame.display.set_mode((self.dwidth, self.dheight))
        self.screen.fill(self.background_color)

    @staticmethod
    def quit_event():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                MultiSocket.set_status(False)
                pygame.quit()
                os.system('exit')
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    MultiSocket.set_status(False)
                    pygame.quit()
                    os.system('exit')
                    sys.exit()

    def set_lock_frame(self, lock: Lock, x_y: tuple):
        img = pygame.image.load(lock.get_last_frame_path()).convert_alpha()
        img = pygame.transform.scale(img, (self.fwidth, self.fheight))
        self.screen.blit(img, x_y)

    def set_lock_text(self, lock: Lock, x_y: tuple):
        x, y = x_y
        text = self.font.render(lock.__str__(), False, self.color)
        self.screen.blit(text, (x + 10, y + self.fheight + 10))

    def run(self):
        while True:
            try:
                x = 0
                y = 0
                counter = 0
                for lock in Lock.objects.all().order_by('port'):
                    counter += 1

                    self.set_lock_frame(lock, (x, y))

                    self.set_lock_text(lock, (x, y))

                    if counter % self.col_count == 0:
                        y += self.fwidth
                        x = 0
                    else:
                        x += self.fwidth
                    if counter > self.col_count * self.row_count:
                        continue

                pygame.display.flip()
                self.quit_event()
            except FileNotFoundError:
                continue
            except pygame.error:
                continue
