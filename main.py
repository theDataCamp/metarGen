import tkinter as tk
from tkinter import ttk
import socket
import time
import datetime
import threading

# Create the Tkinter Application
app = tk.Tk()
app.title("METAR Generator")

# Create Widgets
metar_label = ttk.Label(app, text="METAR:")
metar_text = tk.Text(app, height=5, width=40, wrap=tk.NONE)
x_scrollbar = ttk.Scrollbar(app, orient="horizontal", command=metar_text.xview)
y_scrollbar = ttk.Scrollbar(app, orient="vertical", command=metar_text.yview)
metar_text.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

host_label = ttk.Label(app, text="Host:")
port_label = ttk.Label(app, text="Port:")
host_entry = ttk.Entry(app, width=30)
port_entry = ttk.Entry(app, width=10)
auto_send_var = tk.BooleanVar()
auto_send_checkbox = ttk.Checkbutton(app, text="Automatic Send", variable=auto_send_var)
frequency_label = ttk.Label(app, text="Frequency (mins):")

# Create a ttk variable for the frequency spinner
frequency_var = tk.StringVar()
frequency_spinner = ttk.Spinbox(app, from_=1, to=360, textvariable=frequency_var)
frequency_var.set("1")  # Set the default value to 1

send_button = ttk.Button(app, text="Send Now")
start_button = ttk.Button(app, text="Start Sending")

# Layout Widgets
metar_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
metar_text.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
x_scrollbar.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
y_scrollbar.grid(row=0, column=2, padx=10, pady=5, sticky="ns")
metar_text.grid_propagate(False)
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

host_label.grid(row=1, column=0, padx=10, pady=5)
host_entry.grid(row=1, column=1, padx=10, pady=5)
port_label.grid(row=1, column=2, padx=10, pady=5)
port_entry.grid(row=1, column=3, padx=10, pady=5)
auto_send_checkbox.grid(row=2, column=0, columnspan=4, padx=10, pady=5)
frequency_label.grid(row=3, column=0, padx=10, pady=5)
frequency_spinner.grid(row=3, column=1, padx=10, pady=5)
send_button.grid(row=4, column=0, padx=10, pady=5)
start_button.grid(row=4, column=1, padx=10, pady=5)


# Function to send METAR with correct UTC timestamp
def send_metar_with_timestamp():
    current_time = datetime.datetime.utcnow()
    timestamp = current_time.strftime('%d%H%MZ')
    return timestamp


# Function to send METAR data to the specified host and port
def generate_and_send_metar(host, port):
    with open("input.txt", "r") as file:
        for line in file:
            metar_data = line.strip()

            timestamp = send_metar_with_timestamp()
            metar_data = metar_data.replace('ddHHMMZ', timestamp)

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.sendall(metar_data.encode())
                    metar_text.insert(tk.END, f"Sent METAR: {metar_data}\n")
            except Exception as e:
                metar_text.insert(tk.END, f"Error: {str(e)}\n")


# Function to handle sending METAR data in a separate thread
def send_metar_thread(host, port):
    while auto_send_var.get():
        generate_and_send_metar(host, port)
        time.sleep(int(frequency_var.get()) * 60)


# Function to start sending METAR data in a separate thread
def start_sending_thread():
    host = host_entry.get()
    port = int(port_entry.get())
    thread = threading.Thread(target=send_metar_thread, args=(host, port))
    thread.daemon = True
    thread.start()


# Bind Buttons to Functions
send_button.config(command=lambda: generate_and_send_metar(host_entry.get(), int(port_entry.get())))
start_button.config(command=start_sending_thread)

# Run the Application
app.mainloop()
