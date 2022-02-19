import os
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
    
    def __init__(self, title: str = 'Lock', display_shape=(400, 550), frame_shape=(400, 300),
                 background_color=(255, 255, 255), color=(0, 0, 0), background_img_path = None,
                 icon_path = 'assets/kk.ico', font='serif', font_size=18):
        self.dwidth, self.dheight = display_shape
        self.fwidth, self.fheight = frame_shape
        self.background_color = background_color
        self.color = color
        self.background_img_path = background_img_path

        self.led = Led()
        self.toggle = Toggle()
        self.lock_control = LockControl()
        self.lock_control.set_lock_status(False)
        self.lock_control.set_sensor_status(False)

        pygame.init()
        pygame.font.init()
        pygame.display.set_caption(title)
        pygame.display.set_icon(pygame.image.load(icon_path))
        self.font = pygame.font.SysFont(font, font_size)
        self.screen = pygame.display.set_mode((self.dwidth, self.dheight))
        self.screen.fill(self.background_color)
        self.events_list = []

    def add_event_lisner(self, lisner,*args, **kwargs):
        self.events_list.append((lisner, args, kwargs))        

    def run_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                set_running_status(False)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    set_running_status(False)
            else:
                for lisner, args, kwargs in self.events_list:
                    lisner(event, *args, **kwargs)
    
    def frame_to_surf(self, frame):
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            img_surf = pygame.surfarray.make_surface(frame).convert_alpha()
            img_surf = pygame.transform.scale(img_surf, (self.fwidth - 10, self.fheight - 10))
            return img_surf
        except cv2.error:
            return None

    def render(self, img_surf, lock_status):
        x, y = 0, 0
        if self.background_img_path:
            if os.path.exists(self.background_img_path):
                background_surf = pygame.image.load(self.background_img_path)
                background_surf = pygame.transform.scale(background_surf, (self.dwidth, self.dheight))
                self.screen.blit(background_surf, (x, y))
        x, y = 5, 10
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
        self.led.render(self.screen, (x, y), lock_status)
        # Door led
        door_status = self.lock_control.get_sensor_status()
        x, y = (self.dwidth - 100, y)
        self.led.render(self.screen, (x, y), door_status)
        # Door control text
        x, y = (self.dwidth/2 - 55, y + 40)
        door_lock = self.font.render(self.door_control_text, False, self.color)
        self.screen.blit(door_lock, (x, y))
        # Door control
        door_status = self.lock_control.get_sensor_status()
        x, y = (self.dwidth/2 - 45, y - 10 + 40)
        self.toggle.render(self.screen, (x, y), door_status)

        # Toggle handler 
        def toggle_callback(event, tx_ty=(x, y), tw_th=(self.toggle.iwidth, self.toggle.iheight), lock_status=lock_status , door_status=door_status):
            x, y = event.pos
            tx, ty = tx_ty
            w, h = tw_th
            if tx <= x <= tx + w and ty <= y <= ty + h:
                if lock_status:
                    self.lock_control.set_sensor_status(not door_status)

        self.add_event_lisner(self.toggle.on_click_event, callback=toggle_callback)

        pygame.display.flip()

    def view(self, frame, answer):
        img_surf = self.frame_to_surf(frame)
        self.render(img_surf, answer)
        self.run_events()

