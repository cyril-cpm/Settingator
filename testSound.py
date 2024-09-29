import pygame.mixer as mx
import time

mx.init(channels=1)
sound = mx.Sound("waiting.wav")
good = mx.Sound("good.wav")
channel = mx.Channel(0)

channel.play(sound)
time.sleep(3)
channel.play(good)
time.sleep(3)