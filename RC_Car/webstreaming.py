# import the necessary packages
#import SingleMotionDetector
from pyimagesearch.motion_detection.singlemotiondetector import SingleMotionDetector
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
from flask import request
from car import Car
import threading
import argparse
import datetime
import imutils
import time
import cv2
import json

# GPIO pins for the left motors
# GPIO 23 <-> Dark yellow wire
# GPIO 24 <-> Light yellow wire
# GPIO 18 <-> Black wire
in1 = 23
in2 = 24
en1 = 18

# GPIO pins for the right motors
# GPIO 13 <-> Green wire
# GPIO 6 <-> Blue wire
# GPIO 19 <-> Gray wire
in3 = 13
in4 = 6
en2 = 19

# initialize car
rc = Car(en1, in1, in2, in3, in4, en2)
rc.setup()


autoMotion = True
pwm = 25

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
 
# initialize a flask object
app = Flask(__name__)
 
# initialize the video stream and allow the camera sensor to
# warmup
#vs = VideoStream(usePiCamera=1).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
	# return the rendered template
	return render_template("index.html")

@app.route('/control', methods=['POST']) #GET requests will be blocked
def control():
	global pwm
	button = request.args.get('button')
	if request.args.get('pwm') is not None:
		pwm = int(request.args.get('pwm'))
	motion = request.args.get('motion')
	if motion is not None:
		global autoMotion
		autoMotion = motion.lower() in ("true","1","t")
	if pwm is not None:
		pwm = pwm

	pwmInt = int(pwm)
	if button == 'forward':
		rc.custom_move(1, pwm, 1, pwm)
	elif button == 'backward':
		rc.custom_move(2, pwm, 2, pwm)
	elif button == 'left':
		rc.custom_move(1, 30, 2, 50)
	elif button == 'right':
		rc.custom_move(2, 30, 1, 50)
	elif button == 'stop':
		rc.custom_move(0, 0, 0, 0)
	return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

def detect_ball():
	global outputFrame, lock, pwm, rc

	greenLower = (29,86,6)
	greenUpper = (64, 255, 255)

	centerX = 0

	# keep looping
	while True:
		# grab the current frame
		frame = vs.read()

		if centerX == 0:
			(H,W) = frame.shape[:2]
			# // is for interger operation whereas / is for float
			centerX = W // 2

		# resize the frame
		frame = imutils.resize(frame, width=400)
		if autoMotion:
			# convert frame to the HSV color space
			blurred = cv2.GaussianBlur(frame, (11, 11), 0)
			hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

			# construct a mask for the color "green", then perform
			# a series of dilations and erosions to remove any small
			# blobs left in the mask
			mask = cv2.inRange(hsv, greenLower, greenUpper)
			mask = cv2.erode(mask, None, iterations=2)
			mask = cv2.dilate(mask, None, iterations=2)

			# find contours in the mask and initialize the current
			# (x, y) center of the ball
			cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
			cnts = imutils.grab_contours(cnts)
			#center = None

			# only proceed if at least one contour was found
			if len(cnts) > 0:
				# find the largest contour in the mask, then use
				# it to compute the minimum enclosing circle and
				# centroid
				c = max(cnts, key=cv2.contourArea)
				((x, y), radius) = cv2.minEnclosingCircle(c)
				#M = cv2.moments(c)
				#center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
				#print(radius)
				# only proceed if the radius meets a minimum size
				if radius > 5:
					# draw the circle and centroid on the frame,
					# then update the list of tracked points
					cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
					#cv2.circle(frame, center, 5, (0, 0, 255), -1)

					if x > centerX + radius * 2:
							rc.custom_move(2, pwm, 1, pwm)
						#print("right")
					elif x < centerX - radius * 2:
						#print("left")
						rc.custom_move(1, pwm, 2, pwm)
					elif radius < 50:
						#print("forward")
						rc.custom_move(1, pwm, 1, pwm)
					elif radius > 80:
						#print("back")
						rc.custom_move(2, pwm, 2, pwm)
					else:
						rc.custom_move(0,0,0,0)
				else:
					#print("s")
					rc.custom_move(0,0,0,0)
			else:
				#print("s")
				rc.custom_move(0,0,0,0)

		with lock:
			outputFrame = frame.copy()

def detect_motion(frameCount):
	# grab global references to the video stream, output frame, and
	# lock variables
	global vs, outputFrame, lock, pwm, rc

	# initialize the motion detector and the total number of frames
	# read thus far
	md = SingleMotionDetector(accumWeight=0.1)
	total = 0
	centerX = 0
	reccWidth = 0

	# counter to remove noise. we only perform action when counter is above or below a certain threshhold
	counter = 0

	# loop over frames from the video stream
	while True:
		# read the next frame from the video stream, resize it,
		# convert the frame to grayscale, and blur it
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (7, 7), 0)

		# grab the current timestamp and draw it on the frame
		#timestamp = datetime.datetime.now()
		#cv2.putText(frame, timestamp.strftime(
		#	"%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10),
		#	cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		if centerX == 0:
			(H,W) = frame.shape[:2]
			# // is for interger operation whereas / is for float
			centerX = W // 2
			print(centerX)

		# if the total number of frames has reached a sufficient
		# number to construct a reasonable background model, then
		# continue to process the frame
		if total > frameCount and autoMotion:
			# detect motion in the image
			motion = md.detect(gray)

			# check to see if motion was found in the frame
			if motion is not None:
				# unpack the tuple and draw the box surrounding the
				# "motion area" on the output frame
				(thresh, (minX, minY, maxX, maxY)) = motion
				cv2.rectangle(frame, (minX, minY), (maxX, maxY),
					(0, 0, 255), 2)
				rectWidth = maxX - minX
				midX = (maxX + minX) // 2
				if midX > centerX + rectWidth // 2:
					if counter > 10:
						rc.custom_move(2, 30, 1, 50)
					counter = counter + 1
				elif midX < centerX - rectWidth //2:
					if counter < -10:
						rc.custom_move(1, 30, 2, 50)
					counter = counter - 1
				else:
					rc.custom_move(1, pwm, 1, pwm)
					counter = 0
			else:
				rc.custom_move(0,0,0,0)

		# update the background model and increment the total number
		# of frames read thus far
		md.update(gray)
		total += 1

		# acquire the lock, set the output frame, and release the
		# lock
		with lock:
			outputFrame = frame.copy()

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
 
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
 
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
 
			# ensure the frame was successfully encoded
			if not flag:
				continue
 
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


# check to see if this is the main thread of execution
if __name__ == '__main__':
	# construct the argument parser and parse command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	ap.add_argument("-f", "--frame-count", type=int, default=32,
		help="# of frames used to construct the background model")
	args = vars(ap.parse_args())
 
	# start a thread that will perform motion detection
	#t = threading.Thread(target=detect_motion, args=(
	#	args["frame_count"],))
	t = threading.Thread(target=detect_ball)
	t.daemon = True
	t.start()
 
	# start the flask app
	app.run(host=args["ip"], port=args["port"], debug=False,
		threaded=True, use_reloader=False)
 
# release the video stream pointer
vs.stop()

# Exit cleanly
import atexit
def cleanup():
	print("GPIO cleaned up")
	global rc
	rc.cleanup()
atexit.register(cleanup)
