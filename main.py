import tkinter as tk
from tkinter import ttk
import socket
import datetime
import threading

class HostPortEntryFrame(ttk.Frame):
    def __init__(self, parent, host_label_text, port_label_text):
        super().__init__(parent)
        self.enable_var = tk.IntVar(value=0)
        self.name_label = ttk.Label(self, text="Name")
        self.host_label = ttk.Label(self, text=host_label_text)
        self.port_label = ttk.Label(self, text=port_label_text)
        self.name_entry = ttk.Entry(self, width=30)
        self.host_entry = ttk.Entry(self, width=30)
        self.port_entry = ttk.Entry(self, width=10)
        self.enable_button = ttk.Checkbutton(self, text="Enable", variable=self.enable_var, command=self.toggle_state)

        self.row_num = 0
        self.enable_button.grid(row=self.row_num, column=0, padx=10, pady=5)
        self.row_num += 1
        self.name_label.grid(row=self.row_num, column=0, padx=10, pady=5)
        self.name_entry.grid(row=self.row_num, column=1, padx=10, pady=5)
        self.row_num += 1
        self.host_label.grid(row=self.row_num, column=0, padx=10, pady=5)
        self.host_entry.grid(row=self.row_num, column=1, padx=10, pady=5)
        self.port_label.grid(row=self.row_num, column=2, padx=10, pady=5)
        self.port_entry.grid(row=self.row_num, column=3, padx=10, pady=5)

        self.toggle_state()

    def get_enable_state(self):
        return self.enable_var.get()

    def is_enabled(self):
        return self.enable_var.get() == 1

    def entry_ready_to_send(self):
        return self.is_enabled() and self.get_host() and self.get_port()

    def get_host(self):
        return self.host_entry.get()

    def get_port(self):
        return self.port_entry.get()

    def toggle_state(self):
        new_state = "normal" if self.get_enable_state() == 1 else "disabled"
        self.name_label.config(state=new_state)
        self.name_entry.config(state=new_state)
        self.host_label.config(state=new_state)
        self.host_entry.config(state=new_state)
        self.port_label.config(state=new_state)
        self.port_entry.config(state=new_state)

class METARGeneratorApp(tk.Tk):
    def __init__(self, host_port_pairs):
        super().__init__()
        self.title("METAR Generator")

        # Create Widgets
        self.metar_label = ttk.Label(self, text="Output:")
        self.metar_text = tk.Text(self, height=5, width=40, wrap=tk.NONE)
        self.x_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.metar_text.xview)
        self.y_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.metar_text.yview)
        self.metar_text.configure(xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)

        self.send_button = ttk.Button(self, text="Send Now", command=self.send_now_button_click)

        # Layout Widgets
        self.metar_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.metar_text.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.x_scrollbar.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.y_scrollbar.grid(row=0, column=2, padx=10, pady=5, sticky="ns")
        self.metar_text.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.host_port_entries = []

        # Create host and port input fields based on the dictionary
        for i, (host_label_text, port_label_text) in enumerate(host_port_pairs):
            entry_frame = HostPortEntryFrame(self, host_label_text, port_label_text)
            entry_frame.grid(row=i + 2, column=0, columnspan=4, padx=10, pady=5)
            self.host_port_entries.append(entry_frame)

        self.send_button.grid(row=len(host_port_pairs) + 2, column=0, columnspan=4, padx=10, pady=5)

        # Initialize variables for sending data
        self.file_iterator = None
        self.current_line = None
        self.file_lock = threading.Lock()  # Lock for file reading

    def send_now_button_click(self):
        with self.file_lock:
            if self.file_iterator is None:
                self.file_iterator = self.get_file_iterator()

            try:
                self.current_line = next(self.file_iterator, None)

                if self.current_line is None:
                    self.file_iterator = self.get_file_iterator()
                    self.current_line = next(self.file_iterator, None)

                if self.current_line:
                    for entry_frame in self.host_port_entries:
                        if entry_frame.entry_ready_to_send():
                            host = entry_frame.get_host()
                            port_str = entry_frame.get_port()

                            if host and port_str:
                                try:
                                    port = int(port_str)
                                    thread = threading.Thread(target=self.send_message_to_host, args=(host, port, self.current_line))
                                    thread.start()
                                except ValueError:
                                    self.metar_text.insert(tk.END, f"Invalid port value for {host}\n")
                                except Exception as e:
                                    self.metar_text.insert(tk.END, f"Error: {str(e)}\n")
            except StopIteration:
                self.file_iterator = self.get_file_iterator()
                self.metar_text.insert(tk.END, "Looping back to the beginning of the file.\n")
            except Exception as e:
                self.metar_text.insert(tk.END, f"Error: {str(e)}\n")

    def get_file_iterator(self):
        with open("input.txt", "r") as file:
            for line in file:
                yield line

    def get_timestamp_for_message(self):
        current_time = datetime.datetime.now(datetime.timezone.utc)
        timestamp = current_time.strftime('%d%H%MZ')
        return timestamp

    def send_message_to_host(self, host, port, line):
        metar_data = line.strip()
        timestamp = self.get_timestamp_for_message()
        metar_data = metar_data.replace('ddHHMMZ', timestamp)
        metar_data += '\n'
        metar_data += '\r'

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(metar_data.encode())
                report_type = "METAR" if "METAR" in metar_data else "SPECI"
                self.metar_text.insert(tk.END, f"Sent {report_type} to {host}:{port}: {metar_data}\n")
        except Exception as e:
            self.metar_text.insert(tk.END, f"Error: {str(e)}\n")

if __name__ == "__main__":
    host_port_pairs = [("Host 1:", "Port 1:"), ("Host 2:", "Port 2:"), ("Host 3:", "Port 3:")]
    app = METARGeneratorApp(host_port_pairs)
    app.mainloop()
