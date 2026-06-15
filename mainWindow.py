from tkinter import Tk, Checkbutton, Entry, Button, Frame, Label, BooleanVar, filedialog
from main import main


class MainWindow:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.window = Tk()
        self.window.title("Multi View Player")
        self.window.geometry(f"{screen_width}x{screen_width}")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.on_use_webcam = False
        self.screen = (self.screen_width, self.screen_height)
        self.use_hardware_acceleration = BooleanVar(value=False)
        
        
        self.frm_root = Frame(self.window)
        
        self.chck_webcam = Checkbutton(self.frm_root, text="Use Webcam", command=lambda : self.toggle_webcam())
        self.chck_webcam.pack(padx=10, pady=10)

        self.chck_hardware_acceleration = Checkbutton(
            self.frm_root,
            text="Use Hardware Acceleration (GPU/OpenCL)",
            variable=self.use_hardware_acceleration,
        )
        self.chck_hardware_acceleration.pack(padx=10, pady=10)
        
        self.entry_url = Entry(self.frm_root, width=50, state='disabled')
        self.entry_url.pack(padx=10, pady=10)
        
        self.bttn_select = Button(self.frm_root, text="Select Videos", command=lambda: self.on_select_videos())
        self.bttn_select.pack(padx=10, pady=10)
        
        self.bttn_select_webcam = Button(self.frm_root, text="Use Webcam", command=lambda: self.on_use_webcam())
        self.bttn_select_webcam.pack(padx=10, pady=10)
        
        if self.on_use_webcam:
            self.entry_url.config(state='normal')
            self.bttn_select_webcam.config(state='normal')
            
        else:
            self.entry_url.config(state='disabled')
            self.bttn_select_webcam.config(state='disabled')

        self.frm_root.pack()
        self.window.mainloop()

    def toggle_webcam(self):
        if self.on_use_webcam:
            self.entry_url.config(state='disabled')
            self.bttn_select_webcam.config(state='disabled')
            self.on_use_webcam = False
        else:
            self.entry_url.config(state='normal')
            self.bttn_select_webcam.config(state='normal')
            self.on_use_webcam = True

    def on_select_videos(self):
        video_paths = filedialog.askopenfilenames(
        title="Select Video Files",
        filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
        )
        self.window.withdraw()  # Hide the main window
        videos = list(video_paths)
        main(videos, self.screen, use_gpu=self.use_hardware_acceleration.get())
        
        self.window.deiconify()  # Show the main window again after processing videos
        self.window.update_idletasks()
        

    def on_use_webcam(self):
        url = self.entry_url.get()
        if url:
            video_sources = [url]
            main(video_sources, self.screen)
        else:
            video_sources = [0]  # Use only the webcam
        self.window.withdraw()  # Hide the main window
        
    def on_close(self):
        self.window.destroy()


if __name__ == "__main__":
    screen_width = 800
    main_window = MainWindow(screen_width)
    
