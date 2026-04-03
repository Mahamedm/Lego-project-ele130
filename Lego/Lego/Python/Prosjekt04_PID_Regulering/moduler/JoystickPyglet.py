# For å bruke denne modulen må du ha pyglet installert
# pip install pyglet


from struct import pack
import pyglet
fps = 20



def main(connection=None):
	joystick = None
	joysticks = pyglet.input.get_joysticks()
	if joysticks:
		joystick = joysticks[0]
		joystick.open()
		window = pyglet.window.Window(10, 10, caption="Joystick Pyglet", 
							resizable=True,vsync=False)

		window.minimize() # minimize window 
	
		pyglet.clock.schedule_interval(update,1/fps,joystick=joystick,connection=connection)
		pyglet.app.run()
		print('exit joystick loop on computer',flush=True)
	else:
		print('NO JOYSTICK FOUND',flush=True)


FORMAT = "2d14i2d"
InputList = 18*[0]

def update(dt,joystick=None,connection=None):
	global FORMAT,InputList

	joyForwardInstance = -100*joystick.y
	joySideInstance = 100*joystick.x
	joyTwistInstance = 100*joystick.rz
	joyPotMeterInstance = -100*joystick.z
	
	joyPOVForwardInstance = joystick.hat_y
	joyPOVSideInstance = joystick.hat_x

	joyMainSwitch = joystick.buttons[0]
	joy2Instance = joystick.buttons[1]
	joy3Instance = joystick.buttons[2]
	joy4Instance = joystick.buttons[3]
	joy5Instance = joystick.buttons[4]
	joy6Instance = joystick.buttons[5]
	joy7Instance = joystick.buttons[6]
	joy8Instance = joystick.buttons[7]
	joy9Instance = joystick.buttons[8]
	joy10Instance = joystick.buttons[9]
	joy11Instance = joystick.buttons[10]
	joy12Instance = joystick.buttons[11]


	 #________ INPUTS THAT WILL BE SENT TO EV3 ROBOT _________
	# We know format beforehand and can make efficient struct to send
	# 18 key:string value:floats/int pairs

	InputList[0] = joyForwardInstance
	InputList[1] = joySideInstance


	# toppen av styrestikken
	InputList[2] = joyPOVForwardInstance 
	InputList[3] = joyPOVSideInstance


	# knapper, 1 til 12
	InputList[4] = joyMainSwitch
	InputList[5] = joy2Instance 
	InputList[6] = joy3Instance
	InputList[7] = joy4Instance
	InputList[8] = joy5Instance
	InputList[9] = joy6Instance
	InputList[10] = joy7Instance
	InputList[11] = joy8Instance
	InputList[12] = joy9Instance
	InputList[13] = joy10Instance
	InputList[14] = joy11Instance
	InputList[15] = joy12Instance

	InputList[16] = joyPotMeterInstance
	InputList[17] = joyTwistInstance
	#______________________________________________________


	if connection:
		try:
			connection.send(pack(FORMAT,*InputList))
			msg = connection.recv(1024)
			if msg == b"end?":
				pyglet.app.exit()
		except BlockingIOError:
			pass
		except ConnectionResetError:
			pyglet.app.exit()


	# print("joyForwardInstance: ",joyForwardInstance,flush=True)
	# print("joySideInstance: ",joySideInstance,flush=True)
	# print("joyTwistInstance: ",joyTwistInstance,flush=True)
	# print("joyPotMeterInstance: ",joyPotMeterInstance,flush=True)
	# print(flush=True)
	# print("joyPOVForward: ",joyPOVForwardInstance,flush=True)
	# print("joyPOVSide: ",joyPOVSideInstance,flush=True)
	# print(flush=True)
	# print("joyMainSwitch: ",joyMainSwitch,flush=True)
	# print("joy2Instance: ",joy2Instance,flush=True)
	# print("joy3Instance: ",joy3Instance,flush=True)
	# print("joy4Instance: ",joy4Instance,flush=True)
	# print("joy5Instance: ",joy5Instance,flush=True)

	# print("joy6Instance: ",joy6Instance,flush=True)
	# print("joy7Instance: ",joy7Instance,flush=True)
	# print("joy8Instance: ",joy8Instance,flush=True)
	# print("joy9Instance: ",joy9Instance,flush=True)
	# print("joy10Instance: ",joy10Instance,flush=True)
	# print("joy11Instance: ",joy11Instance,flush=True)
	# print("joy12Instance: ",joy12Instance,flush=True)
	# print(flush=True)


if __name__ == "__main__":
	main()

	

