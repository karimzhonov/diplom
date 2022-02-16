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
    def __init__(self, radius: int = 10, true_color = (0, 255, 0), false_color = (255, 0, 0)) -> None:
        self.radius = radius
        self.true_color = true_color
        self.false_color = false_color
        pygame.init()

    def render(self, screen: pygame.Surface, x_y, answer: bool):
        if answer:
            color = self.true_color
        else:
            color = self.false_color
        
        pygame.draw.circle(screen, (255, 255, 255), x_y, self.radius)
        pygame.draw.circle(screen, color, x_y, self.radius - 2)


class Toggle:
    def __init__(self, scale = 1.2, true_color = (0, 255, 0), 
    false_color = (255, 0, 0), color=(255, 255, 255), border_color=(0, 0, 0)) -> None:
        self.scale = scale
        self.true_color = true_color
        self.false_color = false_color
        self.color = color
        self.border_color = border_color
        
        self.current_button_pos = None
        self.is_checked = None 

    def _set_coordinate_value(self, x_y: tuple[int, int]):
        self.x, self.y = x_y
        self.width, self.height = (40*self.scale, 20*self.scale) 
        self.button_r = self.height / 2 - 2
        self.button_left_x, self.button_left_y = (self.x + 2 + self.button_r, self.y + 2 + self.button_r)   
        self.button_right_x, self.button_right_y = (self.x + self.width - 2 - self.button_r, self.y + 2 + self.button_r)  

    def is_mouse_in_area(self, x, y):
        cx, cy = self.current_button_pos
        r = self.button_r
        if cx - r <= x <= cx + r and cy - r <= y <= cy + r:
            return True
        return False

    def on_click_event(self, event, set_func):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            in_area = self.is_mouse_in_area(x, y)
            if in_area:
                self.is_checked = not self.is_checked
                set_func(self.is_checked)       

    def render(self, screen: pygame.Surface, x_y, answer):
        self._set_coordinate_value(x_y)
        if answer:
            color = self.true_color
            self.current_button_pos = (self.button_right_x, self.button_right_y)
            self.is_checked = True
        else:
            color = self.false_color
            self.current_button_pos = (self.button_left_x, self.button_left_y)
            self.is_checked = False

        # Ellipse
        rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.ellipse(screen, self.color, rect)
        rect = pygame.rect.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4)
        pygame.draw.ellipse(screen, color, rect)
        # Toggle
        pygame.draw.circle(screen, self.border_color, self.current_button_pos, self.button_r)
        pygame.draw.circle(screen, self.color, self.current_button_pos, self.button_r - 2)


