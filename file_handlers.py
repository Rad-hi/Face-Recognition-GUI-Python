import os
import fnmatch
import pickle
import faces_recognizer

#find/create the dir named "KNOWN_FACES_DIRECTORY" in the current dir
KNOWN_FACES_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + "/KNOWN_FACES_DIRECTORY"

def create_file (name) :
	try :
		os.mkdir(KNOWN_FACES_DIRECTORY)
	except FileExistsError:
		pass

def save_encodings (name) :
	with open(f"{KNOWN_FACES_DIRECTORY}/{name}"+".pkl", "wb") as file :
		pickle.dump(faces_recognizer.KNOWN_FACES_ENCODINGS, file)

def load_encodings (name) :
	with open(f"{KNOWN_FACES_DIRECTORY}/{name}", "rb") as file :
		return pickle.load(file)

def load_known_faces () :
	KNOWN_FACES = {}
	try:
		for _,_,files in os.walk(f"{KNOWN_FACES_DIRECTORY}") :
			for f in fnmatch.filter(files,'*.pkl'):
				KNOWN_FACES[os.path.basename(f).split('.')[0]] = load_encodings(os.path.basename(f))
	except :
		pass
	return KNOWN_FACES