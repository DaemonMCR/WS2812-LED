import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import serial
import os

# ---------------- Serial ----------------

ser = serial.Serial("COM3", 115200, timeout=0.1)

# ---------------- Command History ----------------

command_history = []
history_index = -1
ignore_serial_count = 0


# ---------------- Functions ----------------

def write_console(text):
    console.config(state=tk.NORMAL)
    console.insert(tk.END, text)
    console.see(tk.END)
    console.config(state=tk.DISABLED)


def update_values(value=None):
    global ignore_serial

    r = red_slider.get()
    g = green_slider.get()
    b = blue_slider.get()

    r_value.config(text=str(r))
    g_value.config(text=str(g))
    b_value.config(text=str(b))

    ignore_serial = True

    global ignore_serial_count

    ignore_serial_count += 1

    command = f"FILL {r} {g} {b}\n"
    ser.write(command.encode("ascii"))
    ser.flush()


def send_command(event=None):
    global history_index

    command = command_entry.get().strip()

    if command:
        ser.write((command + "\n").encode("ascii"))
        ser.flush()

        write_console(f"> {command}\n")

        command_history.append(command)
        history_index = len(command_history)

    command_entry.delete(0, tk.END)

def save_leds():
    ser.write(b"SAVE\n")
    ser.flush()
    write_console("> SAVE\n")


def load_leds():
    ser.write(b"LOAD\n")
    ser.flush()
    write_console("> LOAD\n")

def clear_console():
    console.config(state=tk.NORMAL)
    console.delete("1.0", tk.END)
    console.config(state=tk.DISABLED)

def previous_command(event=None):
    global history_index

    if command_history:
        if history_index > 0:
            history_index -= 1

        command_entry.delete(0, tk.END)
        command_entry.insert(0, command_history[history_index])

    return "break"


def next_command(event=None):
    global history_index

    if command_history:
        if history_index < len(command_history) - 1:
            history_index += 1

            command_entry.delete(0, tk.END)
            command_entry.insert(0, command_history[history_index])

        else:
            history_index = len(command_history)
            command_entry.delete(0, tk.END)

    return "break"


def read_serial():
    while ser.in_waiting:
        try:
            line = ser.readline().decode("ascii").strip()

            global ignore_serial_count

            if line:
                if ignore_serial_count > 0:
                    ignore_serial_count -= 1
                else:
                    write_console(line + "\n")

        except UnicodeDecodeError:
            pass

    window.after(50, read_serial)


def make_slider(parent, text, command, colour):

    frame = tk.Frame(
        parent,
        bg="#CDCDC1"
    )

    frame.pack(
        fill="x",
        pady=20
    )


    label = tk.Label(
        frame,
        text=text,
        width=8,
        bg="#CDCDC1",
        fg="#3B302A",
        font=("Segoe UI", 11, "bold")
    )

    label.pack(side="left")


    canvas_width = 250
    canvas_height = 40


    canvas = tk.Canvas(
        frame,
        width=canvas_width,
        height=canvas_height,
        bg="#CDCDC1",
        highlightthickness=0
    )

    canvas.pack(side="left")


    value = tk.Label(
        frame,
        text="0",
        width=4,
        bg="#CDCDC1",
        fg="#3B302A"
    )

    value.pack(
        side="left",
        padx=(5, 0)
    )


    track_y = canvas_height // 2


    canvas.create_line(
        15,
        track_y,
        canvas_width - 15,
        track_y,
        fill="#B8AA96",
        width=8,
        capstyle=tk.ROUND
    )


    radius = 10


    knob = canvas.create_oval(
        15 - radius,
        track_y - radius,
        15 + radius,
        track_y + radius,
        fill=colour,
        outline=""
    )


    current_value = {
        "value": 0
    }


    def move_slider(event):

        x = max(
            15,
            min(canvas_width - 15, event.x)
        )


        canvas.coords(
            knob,
            x - radius,
            track_y - radius,
            x + radius,
            track_y + radius
        )


        val = int(
            ((x - 15) / (canvas_width - 30)) * 255
        )


        current_value["value"] = val

        value.config(
            text=str(val)
        )

        command(None)


    canvas.bind(
        "<Button-1>",
        move_slider
    )

    canvas.bind(
        "<B1-Motion>",
        move_slider
    )


    class Slider:
        def get(self):
            return current_value["value"]


    return Slider(), value



# ---------------- Window ----------------

window = tk.Tk()

window.title("WS2812 Controller")
window.geometry("1200x650")


icon_path = os.path.join(
    os.path.dirname(__file__),
    "Assets/tls.ico"
)

window.iconbitmap(icon_path)


window.configure(
    bg="#CDCDC1"
)


window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=3)
window.rowconfigure(0, weight=1)


# ---------------- Left Panel ----------------

left = tk.Frame(
    window,
    bg="#CDCDC1"
)

left.grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=10,
    pady=10
)


tk.Label(
    left,
    text="Serial Command",
    bg="#CDCDC1",
    fg="#3B302A"
).pack(anchor="w")


command_entry = tk.Entry(left)

command_entry.pack(fill="x")


command_entry.bind(
    "<Return>",
    send_command
)

command_entry.bind(
    "<Up>",
    previous_command
)

command_entry.bind(
    "<Down>",
    next_command
)


tk.Label(
    left,
    text="Console",
    bg="#CDCDC1",
    fg="#3B302A"
).pack(
    anchor="w",
    pady=(10, 0)
)


console = ScrolledText(
    left,
    height=20,
    bg="black",
    fg="lime",
    insertbackground="white"
)

console.pack(
    fill="both",
    expand=True
)


console.config(
    state=tk.DISABLED
)


# ---------------- Right Panel ----------------

right = tk.Frame(
    window,
    bg="#CDCDC1"
)

right.grid(
    row=0,
    column=1,
    sticky="nsew",
    padx=10,
    pady=10
)


title = tk.Label(
    right,
    text="RGB Controls",
    font=("Segoe UI", 14, "bold"),
    bg="#CDCDC1",
    fg="#3B302A"
)

title.pack(
    anchor="w",
    pady=(0, 20)
)


red_slider, r_value = make_slider(
    right,
    "Red",
    update_values,
    "#FF5555"
)

green_slider, g_value = make_slider(
    right,
    "Green",
    update_values,
    "#55FF55"
)

blue_slider, b_value = make_slider(
    right,
    "Blue",
    update_values,
    "#5555FF"
)


# ---------------- Save / Load Buttons ----------------

save_load_frame = tk.Frame(
    right,
    bg="#CDCDC1"
)

save_load_frame.pack(
    side="bottom",
    fill="x",
    pady=(0, 10),
    padx=10
)


save_button = tk.Button(
    save_load_frame,
    text="SAVE",
    command=save_leds,
    width=12,
    bg="#E8E3D6",
    fg="#3B302A",
    font=("Segoe UI", 10, "bold")
)


load_button = tk.Button(
    save_load_frame,
    text="LOAD",
    command=load_leds,
    width=12,
    bg="#E8E3D6",
    fg="#3B302A",
    font=("Segoe UI", 10, "bold")
)
save_button.pack(
    side="left",
    padx=(0, 10)
)


load_button.pack(
    side="left",
    padx=(0, 10)
)


clear_button = tk.Button(
    save_load_frame,
    text="CLEAR CONSOLE",
    command=clear_console,
    width=20,
    bg="#E8E3D6",
    fg="#3B302A",
    font=("Segoe UI", 10, "bold")
)

clear_button.pack(
    side="left"
)


# ---------------- Help Box ----------------

help_frame = tk.Frame(
    right,
    bg="#E8E3D6",
    highlightbackground="#B8AA96",
    highlightthickness=1
)

help_frame.pack(
    side="bottom",
    fill="x",
    pady=(0, 10),
    padx=10
)


help_title = tk.Label(
    help_frame,
    text="HELP",
    font=("Segoe UI", 12, "bold"),
    bg="#E8E3D6",
    fg="#3B302A"
)

help_title.pack(
    anchor="w",
    padx=10,
    pady=(8, 0)
)


help_text = tk.Label(
    help_frame,
    text="Enter HELP into the serial command box\n"
         "to display a full list of available commands.",
    justify="left",
    bg="#E8E3D6",
    fg="#3B302A",
    font=("Segoe UI", 10)
)

help_text.pack(
    anchor="w",
    padx=10,
    pady=(5, 10)
)

# ---------------- Initialise ----------------

update_values()
read_serial()

command_entry.focus_set()


# ---------------- Main Loop ----------------

try:
    window.mainloop()

finally:
    ser.close()