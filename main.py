import tkinter as tk
from tkinter import ttk
import socket
import datetime
import threading
import schedule
import time

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

start_button = ttk.Button(app, text="Start Sending", state="disabled")  # Create Start Sending button

send_button = ttk.Button(app, text="Send Now")

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
start_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5)  # Add Start Sending button
send_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5)  # Move Send Now button to row 5

# Create a global variable to track sending status
sending_in_progress = False


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
    global sending_in_progress
    sending_in_progress = True
    auto_send_var.set(False)  # Disable the Automatic Send checkbox
    start_button.config(text="Stop Sending")  # Change button text to Stop Sending

    def send_metar_at_specific_times():
        frequency = int(frequency_var.get())
        schedule.every(frequency).minutes.at(":00").do(lambda: generate_and_send_metar(host, port))
        while sending_in_progress:
            schedule.run_pending()
            time.sleep(1)

    sending_thread = threading.Thread(target=send_metar_at_specific_times)
    sending_thread.daemon = True
    sending_thread.start()


# Function to stop sending METAR data
def stop_sending():
    global sending_in_progress
    sending_in_progress = False
    auto_send_var.set(True)  # Enable the Automatic Send checkbox
    start_button.config(text="Start Sending")  # Change button text to Start Sending


# Function to handle the Start Sending button click
def start_sending_button_click():
    host = host_entry.get()
    port = int(port_entry.get())
    if not sending_in_progress:
        send_metar_thread(host, port)
    else:
        stop_sending()


# Function to handle the Send Now button click
def send_now_button_click(host, port):
    if not auto_send_var.get():  # If automatic sending is disabled
        generate_and_send_metar(host, port)
    else:  # If automatic sending is enabled, send the METAR right away
        generate_and_send_metar(host, port)

# Bind Send Now button to function
send_button.config(command=lambda: send_now_button_click(host_entry.get(), int(port_entry.get())))


# Update GUI based on Automatic Send checkbox
def update_gui_based_on_checkbox():
    if auto_send_var.get():
        start_button.config(state="normal")
    else:
        start_button.config(state="disabled")


auto_send_var.trace_add("write", lambda *args: update_gui_based_on_checkbox())

# Run the Application
app.mainloop()
