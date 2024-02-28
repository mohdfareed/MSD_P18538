"""
Bluetooth controller module.

PyGame is used to interface with the bluetooth controller. The engine launches
a window that must be in focus for events to be captured. This can be resolved
by running a separate python script that captures the events and sends them to
the engine via a socket.
"""
import pygame 

# Initialize Controllers
pygame.joystick.init()
controllers = [
    pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())
]


def start():
    """Start listening to controllers."""

    pygame.init()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Exiting...")
                pygame.quit()
                exit()
            elif event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed: ", event.type)
                print(event.dict)
            elif event.type == pygame.JOYBUTTONUP:
                print("Joystick button released: ", event.type)
                print(event.dict)
            elif event.type == pygame.JOYAXISMOTION:
                print("Joystick axis moved: ", event.type)
                print(event.dict)
            elif event.type == pygame.JOYHATMOTION:
                print("Joystick hat moved: ", event.type)
                print(event.dict)
            elif event.type == pygame.JOYDEVICEADDED:
                print("Joystick device added: ", event.type)
                print(event.dict)
            elif event.type == pygame.JOYDEVICEREMOVED:
                print("Joystick device removed: ", event.type)
                print(event.dict)
            else:
                print("Unknown event: ", event.type)
                print(event.dict)
