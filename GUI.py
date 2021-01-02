#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import gc
import time
#file that contains all the computer vision functionalities
import faces_recognizer  
#file that contains all the read/write fonctionalities
import file_handlers
import os

cap = cv2.VideoCapture(0)

##APP_ICON_PATH = "~/Desktop/security_cam/images/icon.ico" #GUI icon path
PASSWORD_ICON_PATH = os.path.dirname(os.path.realpath(__file__)) + "/images/password_icon.png" #password icon path
APP_WIDTH = 920 #minimal width of the GUI
APP_HEIGHT = 534 #minimal height of the gui
WIDTH  = int(cap.get(3)) #webcam's picture width
HEIGHT = int(cap.get(4)) #wabcam's picture height
#right password to add to the database
VALID_PASSWORD = "password"
#how many face-encodings to be created of each new face 
NUMBER_OF_FACES_ENCODINGS = 1 
NAME_ADDED = False
PASSWORD_ADDED = False
SHOW_PASSWORD = True
RECOGNIZE = False

#The faces are saved as pickle files, it's not actually
#a database, it's a "database"
def add_to_database(KNOWN_FACES, name):
	KNOWN_FACES[name] = faces_recognizer.KNOWN_FACES_ENCODINGS
	file_handlers.create_file(name)
	file_handlers.save_encodings(name)
	#update the current known faces dict with the freshly 
	#added faces' encodings
	KNOWN_FACES = file_handlers.load_known_faces() 
	return KNOWN_FACES

def refresh_database(name):
	KNOWN_FACES = {}
	for _ in range(NUMBER_OF_FACES_ENCODINGS):
		_, frame = cap.read()
		if frame is not None:
			faces_recognizer.KNOWN_FACES_ENCODINGS, NUMBER_OF_FACES_IN_FRAME = faces_recognizer.create_face_encodings(frame)
			#If there's more than one face in the frame, don't
			#consider that a valid face encoding
			if len(faces_recognizer.KNOWN_FACES_ENCODINGS) and NUMBER_OF_FACES_IN_FRAME==1:
				KNOWN_FACES = add_to_database(KNOWN_FACES, name)
				#GUI animation stuff:
				name_entry.delete(0, 'end')
				password_entry.delete(0, 'end')
				password_entry.focus()
				name_entry["state"] = "disabled"
				name_button["state"] = "disabled"
			else:
				#Show a message to the user telling them that
				#there's no valid face to encode
				messagebox.showinfo(message='Either no face, or multiple faces has been detected!\nPlease try again when problem resolved.',
									title = "Invalid name")
				name_entry.delete(0, 'end')
				name_entry.focus()
	return KNOWN_FACES

def add_new_known_face():
	faces_recognizer.KNOWN_FACES = refresh_database(name = NEW_NAME.get().lower())
	faces_recognizer.KNOWN_FACES = file_handlers.load_known_faces()

def display_frames_per_second(frame, start_time):
	END_TIME = abs(start_time-time.time())
	TOP_LEFT = (0,0)
	BOTTOM_RIGHT = (116,26)
	TEXT_POSITION = (8,20)
	TEXT_SIZE = 0.6
	FONT = cv2.FONT_HERSHEY_SIMPLEX
	COLOR = (255,255,0) #BGR
	cv2.rectangle(frame, TOP_LEFT, BOTTOM_RIGHT, (0,0,0), cv2.FILLED)
	cv2.putText(frame, "FPS: {}".format(round(1/max(0.0333,END_TIME),1)), TEXT_POSITION, FONT, TEXT_SIZE,COLOR)
	return frame

#convert a fame object to an image object
def convert_to_image(frame):
	#the screen works with RGB, opencv encodes pictures in BGR
	#so to correctly display the images, color wise, we have
	#to convert them from BGR to RGB 
	frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	image = Image.fromarray(frame)
	return image

def recognize_faces (frame):
	frame = faces_recognizer.identify_faces(frame)
	return frame

######################
#### Main function ###
######################

def update_frame():
	START_TIME = time.time()
	global image
	_, frame = cap.read()
	if frame is not None:
		frame = cv2.flip(frame, 1)
		if RECOGNIZE:
			frame = recognize_faces(frame)
		frame = display_frames_per_second(frame, START_TIME)
		image = convert_to_image(frame)
	photo.paste(image)
	root.after(round(10), update_frame) #update displayed image after: round(1000/FPS) [in milliseconds]

####################################
#### Buttons' callback functions ###
####################################

def name_authentification():
	global NAME_ADDED
	if NEW_NAME.get().lower() in faces_recognizer.KNOWN_FACES.keys() or not len(NEW_NAME.get()):
		messagebox.showinfo(message='Invalid name!\t\nPlease try again.', title = "Invalid name")
		name_entry.delete(0, 'end')
		name_entry.focus()
		NAME_ADDED = False
	if NAME_ADDED:
		return True

def enter_name(*args):
	global NAME_ADDED
	NEW_NAME.get()
	NAME_ADDED = True
	#if the entered name is valid (non empty & non existant in the known faces dir), 
	#allow adding to known faces dir
	if name_authentification(): 
		add_new_known_face()

#This is a pathetic authentification method, but the main goal
#here wasn't immunity to pen-testing practices
def password_authentification():
	global PASSWORD_ADDED
	if PASSWORD.get() != VALID_PASSWORD:
		messagebox.showinfo(message='Invalid password!\t\nPlease try again.', title = "Invalid password")
		password_entry.delete(0, 'end')
		password_entry.focus()
		PASSWORD_ADDED = False
	if PASSWORD_ADDED:
		name_entry["state"] = "normal"
		name_button["state"] = "normal"
		name_entry.focus()

def enter_password(*args):
	global PASSWORD_ADDED
	PASSWORD.get()
	PASSWORD_ADDED = True
	password_authentification()

def take_screenshot():
	try:
		IM = image
		SAVE_PATH = filedialog.asksaveasfilename(defaultextension=".png", filetypes=(("PNG Files", "*.png"), ("All Files", "*.*")))
		IM.save(SAVE_PATH)
	except:
		pass

def show_password():
	global SHOW_PASSWORD
	if SHOW_PASSWORD:
		password_entry["show"] = ''
		SHOW_PASSWORD = False
	else :
		password_entry["show"] = "*"
		SHOW_PASSWORD = True

def enable_recognition():
	global RECOGNIZE
	if RECOGNIZE:
		RECOGNIZE = False
		recognition_button["bg"] = "black"
	else:
		RECOGNIZE = True
		recognition_button["bg"] = "red"

# load all the known faces in the database to the KNOWN_FACES dict
faces_recognizer.KNOWN_FACES = file_handlers.load_known_faces()

# start of GUI
root = tk.Tk()

# general characteristics of the GUI

##root.wm_iconbitmap(APP_ICON_PATH)
root.title("Security Cam")
root.minsize(APP_WIDTH,APP_HEIGHT)
root["bg"]="#131113"

####################
### GUI elements ###
####################

canvas = tk.Canvas(root, width=WIDTH-5, height=HEIGHT-5,bg="black")
canvas.place(relx=0.03,rely=0.052)

recognition_button = tk.Button(canvas, text = "Recognize", command = enable_recognition,
							   bg = "black", fg = "white", activebackground = 'white')
recognition_button.place(relx=0.87,rely=0.93, relwidth=0.12,relheight=0.06)
recognition_button.bind(enable_recognition)
recognition_button.focus()

first_seperator = ttk.Separator(root, orient="horizontal")
first_seperator.place(relx=0.97, rely=0.055,relwidth = 0.2, anchor = "ne")

MESSAGE = tk.StringVar()
MESSAGE.set("To get recognized,\nenter the password!")
message_label=tk.Label(root,textvariable=MESSAGE, wraplength = "5c", bg="white", fg="red")
message_label.place(relx=0.97,rely=0.080,relwidth=0.2,relheight=0.16,anchor="ne")
message_label.config(font=(None, 11))

second_seperator = ttk.Separator(root, orient="horizontal")
second_seperator.place(relx=0.97, rely=0.265,relwidth = 0.2, anchor = "ne")

PASSWORD = tk.StringVar()
password_entry = ttk.Entry(root, textvariable=PASSWORD, show="-")
password_entry.place(relx=0.93, rely=0.290,relheight=0.05,relwidth = 0.16, anchor = "ne")
password_entry.bind('<Return>', enter_password)

password_icon = tk.PhotoImage(file=PASSWORD_ICON_PATH)
show_password_button = tk.Button(root,command=show_password, image= password_icon, border=0, bg="#131113",activebackground="#131113")
show_password_button.place(relx=0.97, rely=0.290,relheight=0.05,relwidth = 0.035, anchor = "ne")
show_password_button.bind(show_password)

password_button=ttk.Button(root,text="Enter password",command=enter_password)
password_button.place(relx=0.97,rely=0.360,relheight=0.05,relwidth=0.2, anchor="ne")
password_button.bind(enter_password)

NEW_NAME = tk.StringVar()
name_entry = ttk.Entry(root, textvariable=NEW_NAME, state="disabled")
name_entry.place(relx=0.97, rely=0.428,relheight=0.05,relwidth = 0.2, anchor = "ne")
name_entry.bind('<Return>', enter_name)

name_button = ttk.Button(root,text="Enter your name",command=enter_name, state="disabled")
name_button.place(relx=0.97,rely=0.498,relheight=0.05,relwidth=0.2,anchor="ne")
name_button.bind(enter_name)

screenshot_button = ttk.Button(root,text="Take a screenshot",command=take_screenshot)
screenshot_button.place(relx=0.97,rely=0.895,relheight=0.05,relwidth=0.2,anchor="ne")
screenshot_button.bind(take_screenshot)

#####################
### Initial frame ###
#####################

_, frame = cap.read()
if frame is not None:
	image = convert_to_image(frame)
	photo = ImageTk.PhotoImage(image=image)
	canvas.create_image(WIDTH, HEIGHT, image=photo, anchor="se")

######################
### Start the show ###
######################

if __name__ == '__main__':
	update_frame()

#create the GUI.
root.mainloop()

#free memory
cap.release()
gc.collect()
