import tkinter as tk

# Create the main window
window = tk.Tk()
window.title("My Tkinter Window")

# Add a label to the window
label = tk.Label(window, text="Hello, Tkinter!")
label.pack()

# Start the Tkinter event loop
window.mainloop()
