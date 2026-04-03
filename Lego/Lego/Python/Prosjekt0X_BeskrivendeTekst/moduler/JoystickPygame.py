# For å bruke denne modulen må du ha pygame installert
# pip install pygame

from struct import pack
import pygame
Dimensions = 500

# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint:
    def __init__(self):                 
        self.reset()
        self.font = pygame.font.Font(None, 25)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (0, 0, 0))
        text_rect = text_bitmap.get_rect(center=(Dimensions//2, self.y))
        screen.blit(text_bitmap, text_rect)
        self.y += self.line_height
    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15



def main(connection=None):
    pygame.init()
    print('Joystick connected to computer is ready to send data',flush=True)
    # Set the width and height of the screen (width, height), and name the window.
    screen = pygame.display.set_mode((500, 500))
    pygame.display.flip()
    pygame.display.set_caption("Joystick")

    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    # Get ready to print.
    text_print = TextPrint()

    # This dict can be left as-is, since pygame will generate a
    # pygame.JOYDEVICEADDED event for every joystick connected
    # at the start of the program.

    FORMAT = "2d14i2d"
    InputList = 18*[0]

    joysticks = {}
    done = False
    while not done:
        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    joystick = joysticks[event.instance_id]

           
            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                if len(joysticks) < 1:
                    # This event will be generated when the program starts for every
                    # joystick, filling up the list without needing to create them manually.
                    joy = pygame.joystick.Joystick(event.device_index)
                    joysticks[joy.get_instance_id()] = joy
                    #print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                if event.instance_id in joysticks:
                    del joysticks[event.instance_id]
                    #print(f"Joystick {event.instance_id} disconnected")

        # Drawing step
        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill((255,237,191))
        text_print.reset()

   
        # For each joystick:
        for joystick in joysticks.values():
            
            text_print.tprint(screen, "")
            # Get the name from the OS for the controller/joystick.
            name = joystick.get_name()
            axes = joystick.get_numaxes()
            buttons = joystick.get_numbuttons()
            text_print.tprint(screen, f"Joystick name: {name}")
            text_print.tprint(screen, "")
            text_print.tprint(screen, "")

            
            
            #________ INPUTS THAT WILL BE SENT TO EV3 ROBOT _________
            # We know format beforehand and can make efficient struct to send
            # 18 key:string value:floats pairs

            InputList[0] = -100*joystick.get_axis(1) # joyForwardInstance
            InputList[1] = 100*joystick.get_axis(0) # joySideInstance


            # toppen av styrestikken
            InputList[2] = joystick.get_hat(0)[1] # joyPOVForwardInstance
            InputList[3] = joystick.get_hat(0)[0] # joyPOVSideInstance


            # knapper, 1 til 12
            InputList[4] = joystick.get_button(0) # joyMainSwitch
            InputList[5] = joystick.get_button(1) # joy2Instance
            InputList[6] = joystick.get_button(2) # joy3Instance
            InputList[7] = joystick.get_button(3) # joy4Instance
            InputList[8] = joystick.get_button(4) # joy5Instance
            InputList[9] = joystick.get_button(5) # joy6Instance
            InputList[10] = joystick.get_button(6) # joy7Instance
            InputList[11] = joystick.get_button(7) # joy8Instance
            InputList[12] = joystick.get_button(8) # joy9Instance
            InputList[13] = joystick.get_button(9) # joy10Instance
            InputList[14] = joystick.get_button(10) # joy11Instance
            InputList[15] = joystick.get_button(11) # joy12Instance
            #______________________________________________________



            # LOGITECH
            if axes == 4:
                InputList[16] = -100*joystick.get_axis(3) # joyPotMeterInstance
                InputList[17] = 100*joystick.get_axis(2) # joyTwistInstance

                text_print.tprint(screen, f"joySide: {100*joystick.get_axis(0):>6.3f}")
                text_print.tprint(screen, "")
                text_print.tprint(screen, f"joyForward: {-100*joystick.get_axis(1):>6.3f}")
                text_print.tprint(screen, "")
                text_print.tprint(screen, f"joyTwist: {100*joystick.get_axis(2):>6.3f}")
                text_print.tprint(screen, "")
                text_print.tprint(screen, f"joyPotMeter: {-100*joystick.get_axis(3):>6.3f}")
                text_print.tprint(screen, "")


            # DACOTA
            if axes == 5:
                
                InputList[16] = -100*joystick.get_axis(3) # joyPotMeterInstance
                InputList[17] = 100*joystick.get_axis(4) # joyTwistInstance

                text_print.tprint(screen, f"joySide: {100*joystick.get_axis(0):>6.3f}")
                text_print.tprint(screen, "")
                text_print.tprint(screen, f"joyForward: {-100*joystick.get_axis(1):>6.3f}")
                text_print.tprint(screen, "")
                text_print.tprint(screen, f"joyTwist: {100*joystick.get_axis(4):>6.3f}")
                text_print.tprint(screen, "")
                text_print.tprint(screen, f"joyPotMeter: {-100*joystick.get_axis(3):>6.3f}")
                text_print.tprint(screen, "")


                

            text_print.tprint(screen, "__________________________")
            text_print.tprint(screen, "")
            text_print.tprint(screen, f"joyPOVForward: {joystick.get_hat(0)[1]}")
            text_print.tprint(screen, "")
            text_print.tprint(screen, f"joyPOVSide: {joystick.get_hat(0)[0]}")
            text_print.tprint(screen, "__________________________")

            text_print.tprint(screen, "")
           
            for i in range(buttons):
                button = joystick.get_button(i)
                if i == 0:
                    text_print.tprint(screen, f"Skyteknapp value: {button}")
                else:
                    text_print.tprint(screen, f"Button {i+1:>2} value: {button}")
            

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        if connection:
            
            try:
                connection.send(pack(FORMAT,*InputList))
                msg = connection.recv(1024)
                if msg == b"end?":
                    pygame.quit()
                    exit()
            except BlockingIOError:
                pass
            except ConnectionResetError:
                pygame.quit()
                exit()

       
        # Limit to x frames per second.
        clock.tick(25)
    pygame.quit()
    exit()

if __name__ == "__main__":
    main()