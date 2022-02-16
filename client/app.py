import cv2
import pygame
import numpy as np
from time import time
from lock_control import LockControl
from config import OPENED_DELAY
from utils import set_running_status, Led, Toggle


class App:
    lock_text = 'Lock status'
    door_text = 'Door status'
    door_control_text = 'Door control'
    t0 = None
    
    def __init__(self, title: str = 'Lock', display_shape=(400, 600), frame_shape=(400, 300),
                 background_color=(0, 0, 0), color=(255, 255, 255)):
        self.dwidth, self.dheight = display_shape
        self.fwidth, self.fheight = frame_shape
        self.background_color = background_color
        self.color = color

        self.led = Led()
        self.lock_control = LockControl()
        self.toggle = Toggle()
        
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(title)
        self.font = pygame.font.SysFont('arial', 18)
        self.screen = pygame.display.set_mode((self.dwidth, self.dheight))
        self.screen.fill(self.background_color)

    def events(self, events: list = None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                set_running_status(False)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    set_running_status(False)
            else:
                if events:
                    for e in events:
                        e(event)

    def door_open_event(self, e):
        self.toggle.on_click_event(e, self.lock_control.set_sensor_status)
    
    def frame_to_surf(self, frame):
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            img_surf = pygame.surfarray.make_surface(frame).convert_alpha()
            img_surf = pygame.transform.scale(img_surf, (self.fwidth, self.fheight))
            return img_surf
        except cv2.error:
            return None

    def render(self, img_surf):
        x, y = 0, 0
        if not img_surf == None:
            self.screen.blit(img_surf, (x, y))
        # Lock text
        x, y = (50, self.fheight + 20)
        text_lock = self.font.render(self.lock_text, False, self.color)
        self.screen.blit(text_lock, (x, y))
        # Door text
        x, y = (self.dwidth - 140, y)
        door_lock = self.font.render(self.door_text, False, self.color)
        self.screen.blit(door_lock, (x, y))
        # Lock led
        x, y = (80, y + 40)
        self.led.render(self.screen, (x, y), self.answer)
        # Door led
        door_status = self.lock_control.get_sensor_status()
        x, y = (self.dwidth - 100, y)
        self.led.render(self.screen, (x, y), door_status)
        # Door control text
        x, y = (self.dwidth/2 - 40, y + 40)
        door_lock = self.font.render(self.door_control_text, False, self.color)
        self.screen.blit(door_lock, (x, y))
        # Door control
        door_status = self.lock_control.get_sensor_status()
        x, y = (self.dwidth/2 - 20, y - 10 + 50)
        self.toggle.render(self.screen, (x, y), door_status)
        
        pygame.display.flip()

    def main_run(self, frame: np.array, event_func_list=None):
        img_surf = self.frame_to_surf(frame)
        self.render(img_surf)
        self.events(event_func_list)

    def run(self):
        while True:
            try:
                self.answer = self.lock_control.get_lock_status()                
                if self.answer:
                    self.t0 = time()
                    # 5 second waiting
                    while time() - self.t0 < OPENED_DELAY:
                        frame = None
                        self.main_run(frame, [self.door_open_event])

                        # if door opened, waiting close the door
                        while self.lock_control.get_sensor_status():
                            frame = None
                            self.main_run(frame, [self.door_open_event])                                
                            
                else:
                    frame = None
                    self.main_run(frame)
                    
            except cv2.error:
                continue


if __name__ == '__main__':
    App().run()
