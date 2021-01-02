import face_recognition
import cv2

MODEL ="hog" #could be either "hog" less accurate than its "cnn" counterpart but faster
#precision of the model, the bigger its tolerance 
#the less accurate it is (between 1 & 0)
TOLERANCE = 0.6 
KNOWN_FACES = {}
KNOWN_FACES_ENCODINGS = []
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.8
FONT_THIKNESS = 1
FRAME_THIKNESS = 2

#factor with which the frame is rescaled in order to 
#speed up the recognition task

#How it's done: 
#	1/ scale down the image by a factor of "SCALER"
#	2/ do the normal recognition process
#	3/ scale up the image to the real size for display
#	4/ multiply the coordinates of the faces found by the scaler
#	   (since they were found in the smaller picture) to place
#	   them correctly in the frame

SCALER = 4 #my pc os this slow, yep :/

def create_face_encodings (frame): 
	KNOWN_FACES_ENCODINGS = []
	try:
		if frame is not None:
			locate_faces = face_recognition.face_locations(frame, model=MODEL, number_of_times_to_upsample=2) # find all faces' locations in the frame
			face_encoded = face_recognition.face_encodings(frame, num_jitters=2) # create the encodings for all found faces in the frame
			KNOWN_FACES_ENCODINGS.append(face_encoded) # populate the faces' encodings list
	except:
		pass
	return KNOWN_FACES_ENCODINGS, len(locate_faces)

def interpret_results(state, name = None):
	if state :
		text = name
		color = (237, 149, 100)
	else:
		text = "Unrecognized"
		color = (0, 0, 255)
	return text, color

def show_results(image, locs, name, location):
	for idx, loc in enumerate(locs):
		if location is not None and idx == location:
			text, color = interpret_results(True, name)
		else:
			text, color = interpret_results(False)
		top_left = (loc[3]*SCALER, loc[0]*SCALER)
		bottom_right = (loc[1]*SCALER, loc[2]*SCALER)

		#Here i'm making the box be dynamically sized depending
		#on the size of the face, but can't go smaller/bigger
		#than a certain size
		height = (loc[1]*SCALER, max(30, SCALER*(loc[0]+int(abs(loc[2]-loc[0])/6))))
		cv2.rectangle(image, top_left, bottom_right, color, FRAME_THIKNESS)
		cv2.rectangle(image, top_left, height, color, cv2.FILLED)
		
		#Same as the size of the rectangle, the text's size 
		#is relative to the face's size in the frame as well
		cv2.putText(image, text,
					(5+loc[3]*SCALER, SCALER*(loc[0]+int(abs(loc[1]-loc[3])/9.5))), 
					FONT, min(FONT_SIZE, abs(loc[3]-loc[1])*SCALER/250), 
					(255,255,255), FONT_THIKNESS)
	return image

def identify_faces(frame): 
	name = None
	location = None
	WIDTH = frame.shape[1]
	HEIGHT = frame.shape[0]
	resized_image = cv2.resize(frame, (int(WIDTH/SCALER),int(HEIGHT/SCALER)))
	locate_faces = face_recognition.face_locations(resized_image, model=MODEL)
	if len(KNOWN_FACES.items()):
		encodings = face_recognition.face_encodings(resized_image, locate_faces)
		for face_encoding in encodings :
			for name, faces in KNOWN_FACES.items():
				result = []
				for face in faces:
					result += face_recognition.compare_faces(face, face_encoding, TOLERANCE)
				if True in result :
					location = result.index(True)
					return show_results(image=frame, locs=locate_faces, name=name.capitalize(), location= location)
	else:
		return show_results(image=frame, locs=locate_faces, name=name, location= location)
	return show_results(image=frame, locs=locate_faces, name=name, location= location)
