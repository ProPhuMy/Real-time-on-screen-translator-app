import sys
import tkinter as tk
from tkinter import ttk
global running
running = False
global has_exit
has_exit = False

if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
    
class SnippingToolGUI:
    def __init__(self):
        self.result = None
        self.root = tk.Tk()
        self.root.title("Screen Region Selector")
        self.root.geometry("300x150")
        self.root.resizable(False, False)
        
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Make window stay on top
        self.root.attributes("-topmost", True)
        
        # Create main frame
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Add title label
        title_label = tk.Label(
            main_frame, 
            text="Screen Region Selector", 
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Add select region button
        self.select_button = tk.Button(
            main_frame,
            text="Select Region",
            command=self.start_selection,
            font=("Arial", 10),
            bg="#0078D4",
            fg="white",
            activebackground="#106EBE",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.select_button.pack()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def start_selection(self):
        global running
        running = True
        self.root.withdraw()
        # Start the region selector
        selector = RegionSelector()
        selector.root.mainloop()
        try:
            selector.root.destroy()
        except Exception:
            pass
        self.result = selector.result
        # Close the main window
        self.root.quit()
    
    def on_close(self):
        global has_exit
        has_exit = True
        self.result = None
        self.root.quit()

class RegionSelector:
    def __init__(self):
        self.result = None
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.25)
        self.root.configure(background="black")
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.rect = None
        self.start_x_screen = self.start_y_screen = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.root.bind("<Escape>", lambda e: self.cancel())

    def on_button_press(self, event):
        # screen coords
        self.start_x_screen = event.x_root
        self.start_y_screen = event.y_root
        # canvas coords
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        cx = self.start_x_screen - root_x
        cy = self.start_y_screen - root_y
        if not self.rect:
            self.rect = self.canvas.create_rectangle(cx, cy, cx, cy, outline="red", width=2)

    def on_move_press(self, event):
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        cur_cx = event.x_root - root_x
        cur_cy = event.y_root - root_y
        if self.rect:
            self.canvas.coords(self.rect, 
                               self.canvas.coords(self.rect)[0],
                               self.canvas.coords(self.rect)[1],
                               cur_cx, cur_cy)

    def on_button_release(self, event):
        end_x = event.x_root
        end_y = event.y_root
        x = min(self.start_x_screen, end_x)
        y = min(self.start_y_screen, end_y)
        w = abs(end_x - self.start_x_screen)
        h = abs(end_y - self.start_y_screen)

        if w == 0 or h == 0:
            self.result = None
        else:
            self.result = (int(x), int(y), int(w), int(h))

        # stop mainloop and close window
        self.root.quit()

    def cancel(self):
        self.result = None
        self.root.quit()

def select_region():
    gui = SnippingToolGUI()
    gui.root.mainloop()
    try:
        gui.root.destroy()
    except Exception:
        pass
    return gui.result

if __name__ == "__main__":
    coords = select_region()
    print("Returned:", coords)
