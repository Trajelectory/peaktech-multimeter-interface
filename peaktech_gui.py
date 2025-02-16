import tkinter as tk
from tkinter import ttk, messagebox, font
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial.tools.list_ports
import threading
from peaktech_utils import decode, shared_data, start_flask_server, stop_flask_server, socketio
import logging

class PeakTechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PeakTech 2025 Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg="#F3F3F3")
        self.root.resizable(False, False)

        self.serial_port = tk.StringVar(value="")
        self.baud_rate = 2400
        self.serial_connection = None
        self.reading = False
        self.data_buffer = []

        self.style = ttk.Style()
        self.configure_style()
        self.digital_font = font.Font(family="Digital-7", size=48, weight="bold")
        self.create_widgets()

    def toggle_flask_widget(self):
        if self.flask_running:
            self.flask_running = False
            stop_flask_server()
            self.btn_toggle_flask.config(text="Widget")
            self.status_label.config(text="Flask Widget: Disabled")
        else:
            self.flask_running = True
            start_flask_server()
            self.btn_toggle_flask.config(text="Widget")
            self.status_label.config(text="Flask Widget: Enabled")


    def configure_style(self):
        self.style.theme_use("clam")
        
        # Style des labels
        self.style.configure("TLabel", font=("Segoe UI", 12), background="#F3F3F3", foreground="#333333")
        
        # Style des boutons
        self.style.configure(
            "TButton",
            font=("Segoe UI", 11),
            padding=6,
            background="#0078D7",
            foreground="#FFFFFF",
            relief="flat"
        )
        self.style.map(
            "TButton",
            background=[("active", "#005A9E")],  # Hover effect
            foreground=[("active", "#FFFFFF")]
        )
        
        # Style des frames
        self.style.configure("TLabelframe", background="#F3F3F3", font=("Segoe UI", 12, "bold"))
        self.style.configure("TLabelframe.Label", background="#F3F3F3", foreground="#0078D7")


    def create_widgets(self):
        # Glyph icons as text
        self.icon_connect = "🔌"  # Unicode for "plug"
        self.icon_disconnect = "❌"  # Unicode for "cross"
        self.icon_flask = "💡"  # Unicode for "light bulb"

        frame_connection = ttk.LabelFrame(self.root, text="Connection Settings", padding=(10, 10))
        frame_connection.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_connection, text="Serial Port:").grid(row=0, column=0, sticky="w")
        self.combo_ports = ttk.Combobox(frame_connection, textvariable=self.serial_port, width=20, state="readonly")
        self.combo_ports.grid(row=0, column=1, padx=5)
        self.refresh_ports()

        ttk.Label(frame_connection, text="Baud Rate:").grid(row=0, column=2, sticky="w")
        self.entry_baud = ttk.Entry(frame_connection, width=10)
        self.entry_baud.insert(0, str(self.baud_rate))
        self.entry_baud.grid(row=0, column=3, padx=5)

        # Bouton CONNECT
        self.btn_connect = ttk.Button(frame_connection, text=f"{self.icon_connect} Connect", command=self.connect_device)
        self.btn_connect.grid(row=0, column=4, padx=5)

        # Bouton DISCONNECT (à côté de CONNECT)
        self.btn_disconnect = ttk.Button(frame_connection, text=f"{self.icon_disconnect} Disconnect", command=self.disconnect_device, state="disabled")
        self.btn_disconnect.grid(row=0, column=5, padx=5)

        self.flask_running = False  # Track the Flask widget state
        self.btn_toggle_flask = ttk.Button(frame_connection, text=f"{self.icon_flask} Widget", command=self.toggle_flask_widget)
        self.btn_toggle_flask.grid(row=0, column=6, padx=5)

        frame_display = ttk.Frame(self.root, padding=(10, 20))
        frame_display.pack(fill="both", expand=True, padx=20, pady=10)

        # Main value and unit display
        self.value_label = tk.Label(frame_display, text="--", font=self.digital_font, fg="#0078D7", bg="#FFFFFF")
        self.value_label.pack(fill="both", expand=True, pady=(10, 5))

        self.status_label = tk.Label(self.root, text="", font=("Segoe UI", 12), bg="#F3F3F3", fg="#555555")
        self.status_label.pack(side="bottom", fill="x", pady=(5, 10))

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Real-Time Data")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Value")
        self.line, = self.ax.plot([], [], "b-", label="Value")
        self.ax.legend(loc="upper left")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.combo_ports["values"] = [port.device for port in ports]
        if ports:
            self.combo_ports.current(0)

    def connect_device(self):
        port = self.serial_port.get()
        baud = self.entry_baud.get()

        try:
            self.serial_connection = serial.Serial(port, int(baud), timeout=1)
            self.reading = True
            self.btn_connect.config(state="disabled")
            self.btn_disconnect.config(state="normal")
            self.start_reading_thread()
        except serial.SerialException as e:
            messagebox.showerror("Connection Error", f"Failed to connect to {port}: {e}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Error: {e}")

    def disconnect_device(self):
        self.reading = False
        if self.serial_connection:
            self.serial_connection.close()
        self.btn_connect.config(state="normal")
        self.btn_disconnect.config(state="disabled")
        self.value_label.config(text="--")
        self.status_label.config(text="")

    def start_reading_thread(self):
        threading.Thread(target=self.read_from_device, daemon=True).start()
        #threading.Thread(target=start_flask_server, daemon=True).start()

    def read_from_device(self):
        while self.reading:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(14)
                    logging.debug(f"Raw data received: {data}")
                    parsed_data = decode(data)
                    if parsed_data:
                        self.update_readings(parsed_data)
            except Exception as e:
                logging.error(f"Error reading from device: {e}")
                self.disconnect_device()
                break

    
    
    def update_readings(self, data):
        value = data.get("value", "--")
        unit = data.get("unit", "")
        status = ", ".join(data.get("status", []))  # Extract the status list

        # Update the shared data for Flask
        shared_data["value"] = value
        shared_data["unit"] = unit
        shared_data["status"] = status

        # Send updated data to clients via WebSocket
        socketio.emit("update", {"value": value, "unit": unit, "status": status})

        # Update GUI
        self.value_label.config(text=f"{value} {unit}")
        self.status_label.config(text=f"Status: {status}")  # Ensure STATUS is updated

        # Update the graph only if the value is numeric
        try:
            numeric_value = float(value)
            self.data_buffer.append(numeric_value)
            if len(self.data_buffer) > 100:
                self.data_buffer.pop(0)
            self.line.set_data(range(len(self.data_buffer)), self.data_buffer)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()
        except ValueError:
            # Skip updating the graph if the value is not numeric (e.g., 'OL')
            pass
