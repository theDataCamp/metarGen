import tkinter as tk
from tkinter import ttk
import socket
import datetime


class METARGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("METAR Generator")

        # Create Widgets
        self.metar_label = ttk.Label(self, text="Output:")
        self.metar_text = tk.Text(self, height=5, width=40, wrap=tk.NONE)
        self.x_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.metar_text.xview)
        self.y_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.metar_text.yview)
        self.metar_text.configure(xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)

        self.host_label = ttk.Label(self, text="Host:")
        self.port_label = ttk.Label(self, text="Port:")
        self.host_entry = ttk.Entry(self, width=30)
        self.port_entry = ttk.Entry(self, width=10)

        self.send_button = ttk.Button(self, text="Send Now", command=self.send_now_button_click)

        # Create checkboxes for CR and LF
        self.add_cr_var = tk.BooleanVar()
        self.add_cr_checkbox = ttk.Checkbutton(self, text="Add CR", variable=self.add_cr_var)
        self.add_lf_var = tk.BooleanVar()
        self.add_lf_checkbox = ttk.Checkbutton(self, text="Add LF", variable=self.add_lf_var)

        # Layout Widgets
        self.metar_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.metar_text.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.x_scrollbar.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.y_scrollbar.grid(row=0, column=2, padx=10, pady=5, sticky="ns")
        self.metar_text.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.host_label.grid(row=2, column=0, padx=10, pady=5)
        self.host_entry.grid(row=2, column=1, padx=10, pady=5)
        self.port_label.grid(row=2, column=2, padx=10, pady=5)
        self.port_entry.grid(row=2, column=3, padx=10, pady=5)
        self.send_button.grid(row=4, column=0, columnspan=4, padx=10, pady=5)

        # Add checkboxes for CR and LF
        self.add_cr_checkbox.grid(row=3, column=0, padx=10, pady=5)
        self.add_lf_checkbox.grid(row=3, column=1, padx=10, pady=5)

        self.file_iterator = None  # Iterator for file lines
        self.current_line = None  # Currently processed line from the file

    def send_now_button_click(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())

        # Initialize the file iterator if not already done
        if self.file_iterator is None:
            self.file_iterator = self.get_file_iterator()

        try:
            # Get the next line from the file
            self.current_line = next(self.file_iterator)

            # Process the line and send METAR
            self.generate_and_send_metar(host, port)
        except StopIteration:
            # Reset the file iterator to loop over lines
            self.file_iterator = self.get_file_iterator()
            self.metar_text.insert(tk.END, "Looping back to the beginning of the file.\n")

    def get_file_iterator(self):
        with open("input.txt", "r") as file:
            for line in file:
                yield line

    def send_metar_with_timestamp(self):
        current_time = datetime.datetime.utcnow()
        timestamp = current_time.strftime('%d%H%MZ')
        return timestamp

    def generate_and_send_metar(self, host, port):
        if self.current_line:
            metar_data = self.current_line.strip()

            timestamp = self.send_metar_with_timestamp()
            metar_data = metar_data.replace('ddHHMMZ', timestamp)

            if self.add_cr_var.get():
                metar_data += "\r"
            if self.add_lf_var.get():
                metar_data += "\n"

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.sendall(metar_data.encode())
                    self.metar_text.insert(tk.END, f"Sent METAR: {metar_data}\n")
            except Exception as e:
                self.metar_text.insert(tk.END, f"Error: {str(e)}\n")
        else:
            self.metar_text.insert(tk.END, "No more lines to send.\n")


if __name__ == "__main__":
    app = METARGeneratorApp()
    app.mainloop()
