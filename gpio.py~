import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

MATRIX = [	[1,2,3,'A'],
							[4,5,6,'B'],
							[7,8,9,'C'],
							['*',0,'#','D']]
							
ROW = [29,31,33,35]
COL = [37,36,38,40]

for j in range(4):
	GPIO.setup(COL[j],GPIO.OUT)
	GPIO.output(COL[j],1)
	
for i in range(4):
	GPIO.setup(ROW[i],GPIO.IN,pull_up_down = GPIO.PUD_UP)

try:
	while(True):
		time.sleep(0.2)
		for j in range(4):
			GPIO.output(COL[j],0)
			for i in range(4):
				if GPIO.input(ROW[i]) == 0:
					print(MATRIX[i][j])
					while(GPIO.input(ROW[i])==0):
						pass
			GPIO.output(COL[j],1)
except KeyboardInterrupt:
	GPIO.cleanup()