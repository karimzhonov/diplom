import os
import sys
import pygame

from main.models import Lock
from main.multi_socket import MultiSocket
from .utils import Toggle, set_pickle, get_pickle, BASE_DIR


class App:
    def __init__(self, title: str = 'Camera surveillance', display_shape=(1000, 600), frame_shape=(200, 150),
                 background_color=(255, 255, 255), color=(0, 0, 0), icon_path=f'{BASE_DIR}/app/assets/kk.ico',
                 font='serif', font_size=18):
        self.dwidth, self.dheight = display_shape
        self.fwidth, self.fheight = frame_shape
        self.background_color = background_color
        self.color = color
        self.col_count = int(self.dwidth / self.fwidth)
        self.row_count = int(self.dheight / self.fheight)
        self.toggle = Toggle(scale=0.2)
        self.events_list = []

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(title)
        pygame.display.set_icon(pygame.image.load(icon_path))
        self.font = pygame.font.SysFont(font, font_size)
        self.screen = pygame.display.set_mode((self.dwidth, self.dheight))
        self.screen.fill(self.background_color)

    def add_event_lisner(self, lisner, *args, **kwargs):
        self.events_list.append((lisner, args, kwargs))

    def run_events(self):
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
            else:
                for lisner, args, kwargs in self.events_list:
                    lisner(event, *args, **kwargs)

    def set_lock_frame(self, lock: Lock, x_y: tuple):
        try:
            img = pygame.image.load(lock.get_last_frame_path()).convert_alpha()
            img = pygame.transform.scale(img, (self.fwidth, self.fheight))
            self.screen.blit(img, x_y)
        except FileNotFoundError:
            pass

    def set_lock_text(self, lock: Lock, x_y: tuple):
        x, y = x_y
        text = self.font.render(lock.__str__(), False, self.color)
        self.screen.blit(text, (x + 10, y + self.fheight + 10))

    def set_toggle_lock_control(self, lock: Lock, x_y):
        x, y = x_y
        x = x + self.fwidth - 100
        y = y + self.fheight + 10
        status, app_control_status = get_pickle(lock.get_last_auth_path())
        self.toggle.render(self.screen, (x, y), status or app_control_status)

        def toggle_callback(event, tx_ty=(x, y), tw_th=(self.toggle.iwidth, self.toggle.iheight)):
            x, y = event.pos
            tx, ty = tx_ty
            w, h = tw_th
            if tx <= x <= tx + w and ty <= y <= ty + h:
                set_pickle(lock.get_last_auth_path(), (status, 1))

        self.add_event_lisner(self.toggle.on_click_event, callback=toggle_callback)

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

                    self.set_toggle_lock_control(lock, (x, y))

                    if counter % self.col_count == 0:
                        y += self.fwidth
                        x = 0
                    else:
                        x += self.fwidth
                    if counter > self.col_count * self.row_count:
                        continue

                pygame.display.flip()
                self.run_events()
            except pygame.error:
                continue
