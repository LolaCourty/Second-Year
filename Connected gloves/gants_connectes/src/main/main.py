# configuration
BUTTON_GPIO = 16
LED_GPIO = 24



def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)


if __name__ == '__main__':

