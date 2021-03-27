import RPi.GPIO as GPIO
from time import sleep

class Car:
  def __init__(self, en1, in1, in2, in3, in4, en2):
    print("init")
    # left motors
    self.en1 = en1
    self.in1 = in1
    self.in2 = in2
    
    # right motors
    self.in3 = in3
    self.in4 = in4
    self.en2 = en2

  def setup(self):
    print("setup")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.in1,GPIO.OUT)
    GPIO.setup(self.in2,GPIO.OUT)
    GPIO.setup(self.en1,GPIO.OUT)
    GPIO.output(self.in1,GPIO.LOW)
    GPIO.output(self.in2,GPIO.LOW)
    GPIO.output(self.en1, GPIO.HIGH)
    self.p=GPIO.PWM(self.en1,1000)
    self.p.start(50)
    self.p.ChangeDutyCycle(50)

    GPIO.setup(self.in3,GPIO.OUT)
    GPIO.setup(self.in4,GPIO.OUT)
    GPIO.setup(self.en2,GPIO.OUT)
    GPIO.output(self.in3,GPIO.LOW)
    GPIO.output(self.in4,GPIO.LOW)
    GPIO.output(self.en2, GPIO.HIGH)
    self.p2=GPIO.PWM(self.en2,1000)
    self.p2.start(50)
    self.p2.ChangeDutyCycle(50)

  # motion (0=stop, 1=forward, 2=backward)
  def custom_move(self, leftMotion, leftDutyCycle, rightMotion, rightDutyCycle):
    if leftMotion == 0:
      GPIO.output(self.in1, GPIO.LOW)
      GPIO.output(self.in2, GPIO.LOW)
    elif leftMotion == 1:
      GPIO.output(self.in1, GPIO.HIGH)
      GPIO.output(self.in2, GPIO.LOW)
    elif leftMotion == 2:
      GPIO.output(self.in1, GPIO.LOW)
      GPIO.output(self.in2, GPIO.HIGH)

    if rightMotion == 0:
      GPIO.output(self.in3, GPIO.LOW)
      GPIO.output(self.in4, GPIO.LOW)
    elif rightMotion == 1:
      GPIO.output(self.in3, GPIO.HIGH)
      GPIO.output(self.in4, GPIO.LOW)
    elif rightMotion == 2:
      GPIO.output(self.in3, GPIO.LOW)
      GPIO.output(self.in4, GPIO.HIGH)

    self.p.ChangeDutyCycle(leftDutyCycle)
    self.p2.ChangeDutyCycle(rightDutyCycle)


  def forward(self):
    GPIO.output(self.in1, GPIO.HIGH)
    GPIO.output(self.in2, GPIO.LOW)
    GPIO.output(self.in3, GPIO.HIGH)
    GPIO.output(self.in4, GPIO.LOW)

  def backward(self):
    GPIO.output(self.in1, GPIO.LOW)
    GPIO.output(self.in2, GPIO.HIGH)
    GPIO.output(self.in3, GPIO.LOW)
    GPIO.output(self.in4, GPIO.HIGH)


  def stop(self):
    GPIO.output(self.in1, GPIO.LOW)
    GPIO.output(self.in2, GPIO.LOW)
    GPIO.output(self.in3, GPIO.LOW)
    GPIO.output(self.in4, GPIO.LOW)

  def cleanup(self):
    GPIO.cleanup()
