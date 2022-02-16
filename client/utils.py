import pickle
import pygame

from config import RUNNONG_PATH


def set_pickle(path, value):
    try:
        with open(path, 'wb') as file:
            pickle.dump(value, file)
    except EOFError:
        set_pickle(path, value)


def get_pickle(path):
    try:
        with open(path, 'rb') as file:
            return pickle.load(file)
    except EOFError:
        return get_pickle(path)


def set_running_status(status):
    set_pickle(RUNNONG_PATH, status)

def get_running_status():
    return get_pickle(RUNNONG_PATH)


class Led:
    true_led_path = 'assets/led_on.png'
    false_led_path = 'assets/led_off.png'
    def __init__(self, raduis=18) -> None:
        self.radius = raduis

    def render(self, screen: pygame.Surface, x_y, status: bool):
        if status:
            path = self.true_led_path
        else:
            path = self.false_led_path
        
        img_surf = pygame.image.load(path)
        img_surf = pygame.transform.scale(img_surf, (self.radius * 2, self.radius * 2))
        x, y = x_y
        x -= self.radius
        y -= self.radius
        screen.blit(img_surf, (x, y))

class Toggle:
    true_toggle_path = 'assets/toggle_on.png'
    false_toggle_path = 'assets/toggle_off.png'
    def __init__(self, scale=0.4) -> None:
        self.scale = scale
        self.is_checked = None

    def is_mouse_in_area(self, x, y):
        if self.x <= x <= self.x + self.iwidth and self.y <= y <= self.y + self.iheight:
            return True
        return False

    def on_click_event(self, event, set_func):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.is_mouse_in_area(x, y):
                self.is_checked = not self.is_checked
                set_func(self.is_checked)       

    def render(self, screen: pygame.Surface, x_y, lock_status):
        if lock_status:
            img_path = self.true_toggle_path
            self.is_checked = True
        else:
            img_path = self.false_toggle_path
            self.is_checked = False
        
        img_surf = pygame.image.load(img_path)
        self.iwidth = img_surf.get_width() * self.scale
        self.iheight = img_surf.get_height() * self.scale
        img_surf = pygame.transform.scale(img_surf, (self.iwidth, self.iheight))
        
        self.x, self.y = x_y
        screen.blit(img_surf, x_y)


