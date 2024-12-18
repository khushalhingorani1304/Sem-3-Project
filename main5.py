import cv2
from keras.models import model_from_json
import pygame
import tkinter as tk
import os

# Flag to control the main loop
running = True
camera_open = False



# Function to open or close the camera
def toggle_camera():
    global camera_open
    if not camera_open:
        camera_open = True
        open_camera_button.config(text="Capture Image")
        # Start updating the camera feed
        update_camera_feed()
    else:
        camera_open = False
        open_camera_button.config(text="Open Camera")










# Function to update the camera feed
def update_camera_feed():
    if camera_open:
        _, im = webcam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(im, 1.3, 5)

        for (p, q, r, s) in faces:
            image = gray[q:q + s, p:p + r]
            cv2.rectangle(im, (p, q), (p + r, q + s), (255, 0, 0), 2)
            image = cv2.resize(image, (48, 48))
            img = image.reshape(1, 48, 48, 1) / 255.0
            pred = model.predict(img)
            prediction_label = labels[pred.argmax()]

            # Play music based on emotion
            if prediction_label in genre_playlists:
                # Clear the current playlist
                playlist.head = None
                # Add songs from the corresponding genre playlist
                for song_path in genre_playlists[prediction_label]:
                    add_song_to_playlist(song_path)
                # Play the first song from the new playlist
                play_current_song()

            cv2.putText(im, '%s' % (prediction_label), (p - 10, q - 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255))

        cv2.imshow("Camera Feed", im)
        key = cv2.waitKey(1)

    if running and camera_open:
        root.after(10, update_camera_feed)  # Continuously update the camera feed



# Load the emotion recognition model
json_file = open("model/Final_AkA_Model.json", "r")
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)
model.load_weights("model/Final_AkA_Model.h5")

# Initializing the emotion labels
labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

# Initialize the webcam
webcam = cv2.VideoCapture(0)
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)

# Initialize pygame for playing music
pygame.mixer.init()

# Create a dictionary for genre-based playlists
genre_playlists = {
    'happy': ['songs/happy/song1.mp3', 'songs/happy/song2.mp3', 'songs/happy/song3.mp3', 'songs/happy/song4.mp3', 'songs/happy/song5.mp3'],
    'sad': ['songs/sad/song1.mp3', 'songs/sad/song2.mp3', 'songs/sad/song3.mp3'],
    'fear': ['songs/fear/song1.mp3'],
    'angry': ['songs/angry/song1.mp3', 'songs/angry/song2.mp3', 'songs/angry/song3.mp3']
}

# Create a circular linked list for the music playlist
class Node:
    def __init__(self, song_path):
        self.song_path = song_path
        self.next = None

class CircularLinkedList:
    def __init__(self):
        self.head = None

    def append(self, song_path):
        new_node = Node(song_path)
        if not self.head:
            self.head = new_node
            new_node.next = self.head
        else:
            current = self.head
            while current.next != self.head:
                current = current.next
            current.next = new_node
            new_node.next = self.head

# Initialize the playlist
playlist = CircularLinkedList()

# Function to add a song to the playlist
def add_song_to_playlist(song_path):
    playlist.append(song_path)

# Function to play the current song
def play_current_song():
    if playlist.head:
        pygame.mixer.music.load(playlist.head.song_path)
        pygame.mixer.music.play()

# Function to play the next song
def play_next_song():
    if playlist.head:
        playlist.head = playlist.head.next
        play_current_song()

# Function to stop the music
def stop_music():
    pygame.mixer.music.stop()

# Music control functions
is_paused = False

def play():
    global is_paused
    if is_paused:
        pygame.mixer.music.unpause()
        is_paused = False
    else:
        play_current_song()

def pause():
    global is_paused
    pygame.mixer.music.pause()
    is_paused = True

# Function to stop the application gracefully
def stop_application():
    global running
    running = False
    stop_music()
    root.quit()

# Create a tkinter GUI
root = tk.Tk()
root.title("Emotion-Based Music Player")

# Set the initial window size
root.geometry("640x480")

# Set the background color
root.configure(bg="#013220")

# Create a header label with the highlighted color
header_label = tk.Label(root, text="EmoTunes", font=("Helvetica", 24, "bold underline"), bg="#013220", fg="white")
header_label.pack(pady=10)

# Create a frame for the buttons on the left
left_button_frame = tk.Frame(root, bg="#013220")
left_button_frame.pack(side=tk.LEFT, padx=10, pady=20)

# Open Camera button on the left
open_camera_button = tk.Button(left_button_frame, text="Open Camera", command=toggle_camera)
open_camera_button.pack()

# Create a frame for the buttons on the right
right_frame = tk.Frame(root, bg="#013220")
right_frame.pack(side=tk.RIGHT, padx=10, pady=20)

# Create a label for the "Music Player" text with a visible background color
music_player_label = tk.Label(
    right_frame,
    text="Music Player",
    font=("Helvetica", 12),
    bg="#1E6035",
    fg="white",
    width=20,
    height=2
)
music_player_label.pack()

# Create a frame for the "Music Player" label and buttons with a black border
music_player_frame = tk.Frame(right_frame, bg="black", bd=2, relief=tk.RIDGE)
music_player_frame.pack(pady=10, padx=10)

# Create and pack the "Play," "Pause," "Next," and "Quit" buttons in a single line within "Music Player"
play_button = tk.Button(music_player_frame, text="▶", command=play_current_song, padx=10, fg="Red")
play_button.pack(side=tk.LEFT, padx=5)

pause_button = tk.Button(music_player_frame, text="⏸", command=pause, padx=10)
pause_button.pack(side=tk.LEFT, padx=5)

next_button = tk.Button(music_player_frame, text="⏭️", command=play_next_song, padx=10, fg="blue")
next_button.pack(side=tk.LEFT, padx=5)

quit_button = tk.Button(music_player_frame, text="Quit", command=stop_application, padx=10)
quit_button.pack(side=tk.LEFT, padx=5)


# Start the tkinter main loop
root.mainloop()

# Cleanup when exiting the loop
cv2.destroyAllWindows()
