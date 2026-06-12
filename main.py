import cv2
import time
import os
import numpy as np
from tkinter import Tk, Frame, Button, Label, Checkbutton, Entry
from tkinter import filedialog



def main(video_sources, screen_width):
    # Open a VideoCapture for each source (file path or device index)
    caps = [cv2.VideoCapture(src) for src in video_sources]

    if not any(cap.isOpened() for cap in caps):
        print("Error: None of the video sources could be opened.")
        for cap in caps:
            cap.release()
        return

    # Determine a reasonable FPS from the first opened capture
    fps = 30.0
    for cap in caps:
        if cap.isOpened():
            framerate = cap.get(cv2.CAP_PROP_FPS)
            if framerate and framerate > 0:
                fps = framerate
            break
    wait_time = 1.0 / fps if fps > 0 else 1.0 / 30

    while True:
        start = time.perf_counter()
        frames = []

        for cap, src in zip(caps, video_sources):
            if not cap.isOpened():
                frames.append(None)
                continue

            ret, frame = cap.read()
            if not ret or frame is None:
                # Fallback: if path exists and is an image, try imread once
                if os.path.isfile(src):
                    img = cv2.imread(src)
                    frame = img
                else:
                    frame = None
            frames.append(frame)

        # If all frames are None, stop
        if all(f is None for f in frames):
            print("Error: no frames available from any source. Exiting.")
            break

        # Ensure we have 4 tiles (pad with None if fewer sources)
        while len(frames) < 4:
            frames.append(None)

        def to_tile(f):
            screen_width = screen[0] / 2
            screen_height = screen[1] / 2
            tile_width = int(screen_width)
            tile_height = int(screen_height) 
            
            if f is None:
                return 255 * np.ones((tile_height, tile_width, 3), dtype=np.uint8)
            return cv2.resize(f, (tile_width, tile_height))

        tiles = [to_tile(frames[i]) for i in range(4)]

        row1 = cv2.hconcat([tiles[0], tiles[1]])
        row2 = cv2.hconcat([tiles[2], tiles[3]])
        combined = cv2.vconcat([row1, row2])

        cv2.imshow('Video Stream', combined)

        # Maintain approximate framerate
        progress = (time.perf_counter() - start)
        sleep_time = max(0, wait_time - progress)
        time.sleep(sleep_time)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    video_paths = []
    root = Tk()
    frm_root = Frame(root)
    label = Label(frm_root, text="Select video files to display in a 2x2 grid. Press 'q' to quit.")
    label.pack(padx=10, pady=10)
    use_webcam = False
    
 
    chck_webcam = Checkbutton(frm_root, text="Use Webcam", command=lambda : toggle_webcam())
    chck_webcam.pack(padx=10, pady=10)
    
    entry_url = Entry(frm_root, width=50, state='disabled')
    entry_url.pack(padx=10, pady=10)
    
    bttn_select = Button(frm_root, text="Select Videos", command=lambda: on_select_videos())
    bttn_select.pack(padx=10, pady=10)
    
    bttn_select_webcam = Button(frm_root, text="Use Webcam", command=lambda: on_use_webcam())
    bttn_select_webcam.pack(padx=10, pady=10)
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    screen = (screen_width, screen_height)
    
    def toggle_webcam():
        global use_webcam
        
        if use_webcam:
            entry_url.config(state='disabled')
            bttn_select_webcam.config(state='disabled')
            use_webcam = False
        else:
            entry_url.config(state='normal')
            bttn_select_webcam.config(state='normal')
            use_webcam = True
    
    
    
    if use_webcam:
        entry_url.config(state='normal')
        bttn_select_webcam.config(state='normal')
        
    else:
        entry_url.config(state='disabled')
        bttn_select_webcam.config(state='disabled')
    
   
    def on_select_videos():
        video_paths = filedialog.askopenfilenames(
        title="Select Video Files",
        filetypes=[("Video files", "*.bik")]
        )
        root.withdraw()  # Hide the main window
        videos = list(video_paths)
        main(videos, screen)
        
        root.deiconify()  # Show the main window again after processing videos
        root.update_idletasks()
        
    
    def on_use_webcam():
        url = entry_url.get()
        if url:
            video_sources = [url]
            main(video_sources, screen)
        else:
            video_sources = [0]  # Use only the webcam
        root.withdraw()  # Hide the main window

    frm_root.pack()
    root.mainloop()
    
