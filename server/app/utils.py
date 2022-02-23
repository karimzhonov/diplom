import pygame

from server.settings import BASE_DIR

class Toggle:
    true_toggle_path = f'{BASE_DIR}/app/assets/toggle_on.png'
    false_toggle_path = f'{BASE_DIR}/app/assets/toggle_off.png'
    def __init__(self, scale=0.4) -> None:
        self.scale = scale
        self.is_checked = None
        self.iwidth = None
        self.iheight = None
        self.x = None
        self.y = None

    @staticmethod
    def on_click_event(event, callback):
        if event.type == pygame.MOUSEBUTTONDOWN:
            callback(event)
            

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