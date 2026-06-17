from tkinter import Tk, Checkbutton, Entry, Button, Frame, Label, BooleanVar, filedialog, Listbox, END, SINGLE, messagebox
import json
import os
from main import main


class MainWindow:
    def __init__(self, screen_width):
        self.screen_width = screen_width
        self.window = Tk()
        self.window.title("Multi View Player")
        #self.window.geometry(f"{screen_width}x{screen_width}")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.use_webcam = True
        self.screen = (self.screen_width, self.screen_height)
        self.use_hardware_acceleration = BooleanVar(value=False)
        
        self.frm_options = Frame(self.window, bd=2, relief='groove')
        self.frm_fields_left = Frame(self.window, bd=2, relief='groove')
        self.frm_fields_right = Frame(self.window, bd=2, relief='groove')
        
        
        self.frm_root = Frame(self.window)
        
        self.chck_webcam = Checkbutton(self.frm_options, text="Use Webcam", indicatoron=True, command=lambda : self.toggle_webcam())
        self.chck_webcam.pack(padx=10, pady=10, side='left', anchor='nw')
        self.chck_webcam.select()  # Default to using webcam

        self.chck_hardware_acceleration = Checkbutton(
            self.frm_options,
            text="Use Hardware Acceleration (GPU/OpenCL)",
            variable=self.use_hardware_acceleration,
        )
        self.chck_hardware_acceleration.pack(padx=10, pady=10, side='right', anchor='nw')
        
        self.entry_url = Entry(self.frm_fields_right, width=50, state='normal')
        self.entry_url.pack(padx=10, pady=10)
        
        
        # Listbox to show multiple URLs
        self.lbl_urls = Label(self.frm_fields_left, text="URLs:")
        self.lbl_urls.pack(padx=10, pady=(5, 0))
        
        self.listbox_urls = Listbox(self.frm_fields_left, selectmode=SINGLE, width=80, height=6)
        self.listbox_urls.pack(padx=10, pady=5)

        self.frm_btt_left = Frame(self.frm_fields_left)
        # Buttons to manage URLs
        self.bttn_add_url = Button(self.frm_btt_left, text="Add URL", command=lambda: self.add_url(), width=15)
        self.bttn_add_url.pack(padx=5, pady=2, side='left')

        self.bttn_edit_url = Button(self.frm_btt_left, text="Edit Selected", command=lambda: self.edit_selected(), width=15)
        self.bttn_edit_url.pack(padx=5, pady=2, side='left')

        self.bttn_remove_url = Button(self.frm_btt_left, text="Remove Selected", command=lambda: self.remove_selected(), width=15)
        self.bttn_remove_url.pack(padx=5, pady=2, side='left')

        self.bttn_save_urls = Button(self.frm_btt_left, text="Save URLs", command=lambda: self.save_urls(), width=15)
        self.bttn_save_urls.pack(padx=5, pady=2, side='left')
        self.bttn_save_default = Button(self.frm_btt_left, text="Save to urls.json", command=lambda: self.save_default_urls(), width=15)
        self.bttn_save_default.pack(padx=5, pady=2, side='bottom')

        self.frm_btt_left.pack(padx=10, pady=5, expand=True, fill='x')

        self.frm_btt_right = Frame(self.frm_fields_right)
        self.bttn_load_urls = Button(self.frm_btt_right, text="Load URLs", command=lambda: self.load_urls(), width=15)
        self.bttn_load_urls.pack(padx=5, pady=2, side='left')

        self.bttn_open_urls = Button(self.frm_btt_right, text="Open URLs", command=lambda: self.open_urls(), width=15)
        self.bttn_open_urls.pack(padx=5, pady=6, side='left')
        
        self.bttn_select = Button(self.frm_btt_right, text="Select Videos", command=lambda: self.on_select_videos(), width=15)
        self.bttn_select.pack(padx=10, pady=10, side='left')
        
        self.bttn_select_webcam = Button(self.frm_btt_right, text="Use Webcam", command=lambda: self.on_use_webcam(), width=15)
        self.bttn_select_webcam.pack(padx=10, pady=10, side='left')
        
        self.frm_bttn_start = Frame(self.frm_fields_right, bd=2, relief='groove')
        self.bttn_start = Button(self.frm_bttn_start, text="Start", bg='green', fg='white', command=lambda: self.open_urls())
        self.bttn_start.pack(padx=10, pady=10, expand=True, fill='both')
        
        self.frm_options.pack(expand=True, fill='x')
        self.frm_fields_left.pack(side='left', expand=True, fill='y')
        self.frm_fields_right.pack(side='left', expand=True, fill='y')

        self.frm_btt_left.pack()
        self.frm_btt_right.pack()
        self.frm_bttn_start.pack(side='bottom', expand=True, fill='both')
        
        if self.use_webcam:
            self.bttn_select_webcam.config(state='normal')
        else:
            self.bttn_select_webcam.config(state='disabled')

        self.frm_root.pack()
        # default urls file in working directory
        self.default_urls_file = os.path.join(os.getcwd(), 'urls.json')
        # try auto-load default URLs
        self.load_default_urls()
        self.window.mainloop()

    def toggle_webcam(self):
        if self.use_webcam:
            self.entry_url.config(state='disabled')
            self.bttn_select_webcam.config(state='disabled')
            self.use_webcam = False
        else:
            self.entry_url.config(state='normal')
            self.bttn_select_webcam.config(state='normal')
            self.use_webcam = True

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
            self.window.withdraw()
            main(video_sources, self.screen)
            self.window.deiconify()
        else:
            video_sources = [0]  # Use only the webcam
            self.window.withdraw()
            main(video_sources, self.screen)
            self.window.deiconify()

    def add_url(self):
        url = self.entry_url.get().strip()
        if not url:
            messagebox.showwarning("Add URL", "Please enter a URL before adding.")
            return
        self.listbox_urls.insert(END, url)
        self.entry_url.delete(0, END)

    def remove_selected(self):
        sel = self.listbox_urls.curselection()
        if not sel:
            messagebox.showwarning("Remove URL", "Select a URL to remove.")
            return
        self.listbox_urls.delete(sel[0])

    def edit_selected(self):
        sel = self.listbox_urls.curselection()
        if not sel:
            messagebox.showwarning("Edit URL", "Select a URL to edit.")
            return
        idx = sel[0]
        val = self.listbox_urls.get(idx)
        self.listbox_urls.delete(idx)
        self.entry_url.delete(0, END)
        self.entry_url.insert(0, val)

    def save_urls(self):
        urls = list(self.listbox_urls.get(0, END))
        if not urls:
            messagebox.showwarning("Save URLs", "No URLs to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files','*.json')])
        if not file_path:
            return
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(urls, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Save URLs", f"Saved {len(urls)} URLs to {file_path}")
        except Exception as e:
            messagebox.showerror("Save URLs", f"Error saving URLs: {e}")

    def load_urls(self):
        file_path = filedialog.askopenfilename(filetypes=[('JSON files','*.json'), ('All files','*.*')])
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                messagebox.showerror("Load URLs", "JSON file must contain a list of URLs.")
                return
            self.listbox_urls.delete(0, END)
            for u in data:
                self.listbox_urls.insert(END, str(u))
            messagebox.showinfo("Load URLs", f"Loaded {len(data)} URLs from {file_path}")
        except Exception as e:
            messagebox.showerror("Load URLs", f"Error loading URLs: {e}")

    def load_default_urls(self):
        if not os.path.exists(self.default_urls_file):
            return
        try:
            with open(self.default_urls_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                return
            self.listbox_urls.delete(0, END)
            for u in data:
                self.listbox_urls.insert(END, str(u))
        except Exception:
            return

    def save_default_urls(self):
        urls = list(self.listbox_urls.get(0, END))
        if not urls:
            messagebox.showwarning("Save URLs", "No URLs to save.")
            return
        try:
            with open(self.default_urls_file, 'w', encoding='utf-8') as f:
                json.dump(urls, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Save URLs", f"Saved {len(urls)} URLs to {self.default_urls_file}")
        except Exception as e:
            messagebox.showerror("Save URLs", f"Error saving URLs: {e}")

    def open_urls(self):
        urls = list(self.listbox_urls.get(0, END))
        if not urls:
            messagebox.showwarning("Open URLs", "No URLs to open. Add or load URLs first.")
            return
        self.window.withdraw()
        main(urls, self.screen, use_gpu=self.use_hardware_acceleration.get())
        self.window.deiconify()
        
    def on_close(self):
        self.window.destroy()


if __name__ == "__main__":
    screen_width = 800
    main_window = MainWindow(screen_width)
    
