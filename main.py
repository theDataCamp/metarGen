import tkinter as tk
from tkinter import ttk
import socket
import time
import datetime

# Create the Tkinter Application
app = tk.Tk()
app.title("METAR Generator")

# Create Widgets
metar_label = ttk.Label(app, text="METAR:")
metar_text = tk.Text(app, height=5, width=40)
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
metar_text.grid(row=0, column=1, columnspan=3, padx=10, pady=5)
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
    # Get the current UTC time and format it as 'ddHHMMZ'
    current_time = datetime.datetime.now(datetime.UTC)
    timestamp = current_time.strftime('%d%H%MZ')
    return timestamp


# Function to send METAR data to the specified host and port
def generate_and_send_metar(host, port):
    with open("input.txt", "r") as file:
        for line in file:
            # Read METAR data from the input file
            metar_data = line.strip()

            # Update the timestamp with the current UTC time
            timestamp = send_metar_with_timestamp()
            metar_data = metar_data.replace('ddHHMMZ', timestamp)

            # Send METAR data to the specified host and port
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.sendall(metar_data.encode())
                    metar_text.insert(tk.END, f"Sent METAR: {metar_data}\n")
            except Exception as e:
                metar_text.insert(tk.END, f"Error: {str(e)}\n")


# Start Automatic Sending
def start_automatic_sending(host, port):
    frequency = int(frequency_var.get())
    while auto_send_var.get():
        generate_and_send_metar(host, port)
        time.sleep(frequency * 60)


# Bind Buttons to Functions
send_button.config(command=lambda: generate_and_send_metar(host_entry.get(), int(port_entry.get())))
start_button.config(command=lambda: start_automatic_sending(host_entry.get(), int(port_entry.get())))

# Run the Application
app.mainloop()
