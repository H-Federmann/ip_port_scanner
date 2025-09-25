import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import socket
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import os
import shutil
import sys

#=============== Helper functions
def ping_host(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(["ping", param, "1", ip],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False

#=============== Helper function: scan port
def scan_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            result = s.connect_ex((ip, port))
            return result == 0
    except Exception:
        return False

#=============== Helper function: resolve hostname
def resolve_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "Unknown"

#=============== Console cat animation (adapted from your cat.py)
def cat_animation(stop_event, delay=0.08):
    """
    Runs an ASCII cat animation in the console until stop_event is set.
    This function clears the console each frame. Designed to run in a thread.
    """
    frames_right = [
        [r"   (\_._/)  ", r"   ( o o )  ", r" ~  < ^ <  "],
        [r"   (\_._/)  ", r"   ( o o )  ", r" ~~ < v <  "],
        [r"   (\^.^/)  ", r"   ( o o )  ", r" ~  < ^ v  "],
        [r"   (\^.^/)  ", r"   ( o o )  ", r" ~~ < v ^  "],
        [r"   (\_._/)  ", r"   ( o o )  ", r" ~  < v <  "],
        [r"   (\^.^/)  ", r"   ( o o )  ", r" ~~ < ^ v  "]
    ]

    frames_left = [
        [r"  (\_._/)   ", r"  ( o o )   ", r"  > ^ <  ~ "],
        [r"  (\_._/)   ", r"  ( o o )   ", r"  > v <  ~~"],
        [r"  (\^.^/)   ", r"  ( o o )   ", r"  > ^ v  ~ "],
        [r"  (\^.^/)   ", r"  ( o o )   ", r"  > v ^  ~~"],
        [r"  (\_._/)   ", r"  ( o o )   ", r"  > v <  ~ "],
        [r"  (\^.^/)   ", r"  ( o o )   ", r"  > ^ v  ~~"]
    ]

    width = shutil.get_terminal_size(fallback=(80, 20)).columns
    cat_width = max(len(line) for frame in frames_right for line in frame)

    direction = 1
    position = 0 if direction == 1 else max(0, width - cat_width)
    frame_index = 0

    clear_cmd = "cls" if platform.system().lower() == "windows" else "clear"

    # If the Python process wasn't started from a console (e.g. double-clicked),
    # writes to stdout will likely be invisible. We still run harmlessly.
    try:
        while not stop_event.is_set():
            # Recompute width in case terminal resized
            width = shutil.get_terminal_size(fallback=(80, 20)).columns
            frame = frames_right[frame_index] if direction == 1 else frames_left[frame_index]

            # clear console
            os.system(clear_cmd)

            # print blank lines at top for nicer separation (optional)
            # print("\n" * 0, end="")

            # print cat with current position
            for line in frame:
                # ensure position does not exceed bounds
                pos = max(0, min(position, max(0, width - cat_width)))
                sys.stdout.write(" " * pos + line + "\n")
            sys.stdout.flush()

            # next frame
            frame_index = (frame_index + 1) % len(frames_right)

            # move position
            position += direction

            # change direction when reaching edges
            if direction == 1 and position + cat_width >= width:
                direction = -1
                position = max(0, width - cat_width)
            elif direction == -1 and position <= 0:
                direction = 1
                position = 0

            # wait
            time.sleep(delay)
    except Exception:
        # swallow exceptions on shutdown
        pass
    finally:
        # clear console once more on exit (optional)
        try:
            os.system(clear_cmd)
        except Exception:
            pass

#=============== Main App Class
class ScannerApp:
#=============== Header
    def __init__(self, root):
        self.root = root
        self.root.title("IP & Port Scanner")
        self.root.geometry("950x600")

#=============== Create stop event and start cat animation thread
        self._cat_stop_event = threading.Event()
        self._cat_thread = threading.Thread(target=cat_animation, args=(self._cat_stop_event,), daemon=True)
        self._cat_thread.start()

#=============== Bind WM_DELETE to stop cat + close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

#=============== Hotkeys
        root.bind("<Control-x>", lambda event: self.start_scan())
        root.bind("<Control-c>", lambda event: self.stop_scan())
        root.bind("<Control-s>", lambda event: self.export_csv())

#=============== Header with ASCII cat (GUI) and title centered
        header_frame = ttk.Frame(root)
        header_frame.pack(pady=10, fill="x")

        cat_lines = [r" /\_/\ ", r"( o.o )", r" > ^ < "]
        for i, line in enumerate(cat_lines):
            tk.Label(header_frame, text=line, font=("Consolas", 12)).grid(row=i, column=0, sticky="w")

        title_label = ttk.Label(header_frame, text="IP & Port Scanner", font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=1, rowspan=len(cat_lines), sticky="n", padx=10)
        header_frame.grid_columnconfigure(1, weight=1)

#=============== Input Frame
        input_frame = ttk.Frame(root, padding=10)
        input_frame.pack(fill="x")

        ttk.Label(input_frame, text="Start IP:").grid(row=0, column=0, sticky="w")
        self.start_ip = ttk.Entry(input_frame)
        self.start_ip.insert(0, "192.168.178.1")
        self.start_ip.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="End IP:").grid(row=0, column=2, sticky="w")
        self.end_ip = ttk.Entry(input_frame)
        self.end_ip.insert(0, "192.168.178.10")
        self.end_ip.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Start Port:").grid(row=1, column=0, sticky="w")
        self.start_port = ttk.Entry(input_frame)
        self.start_port.insert(0, "20")
        self.start_port.grid(row=1, column=1, padx=5)

        ttk.Label(input_frame, text="End Port:").grid(row=1, column=2, sticky="w")
        self.end_port = ttk.Entry(input_frame)
        self.end_port.insert(0, "1024")
        self.end_port.grid(row=1, column=3, padx=5)

        self.scan_btn = ttk.Button(input_frame, text="Start Scan", command=self.start_scan)
        self.scan_btn.grid(row=0, column=4, rowspan=2, padx=10, pady=5)

        self.stop_btn = ttk.Button(input_frame, text="Stop Scan", command=self.stop_scan, state="disabled")
        self.stop_btn.grid(row=0, column=5, rowspan=2, padx=10, pady=5)

#=============== Results Frame with vertical scrollbar
        result_frame = ttk.LabelFrame(root, text="Scan Results", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.status_label = ttk.Label(result_frame, text="", font=("Segoe UI", 10, "italic"))
        self.status_label.pack(anchor="w", pady=(0, 5))

        scroll_frame = ttk.Frame(result_frame)
        scroll_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(scroll_frame, columns=("IP", "Hostname", "Port", "Status"), show="headings")
        self.tree.heading("IP", text="IP Address")
        self.tree.heading("Hostname", text="Hostname")
        self.tree.heading("Port", text="Port")
        self.tree.heading("Status", text="Status")

        vsb = ttk.Scrollbar(scroll_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)

#=============== Progress bar with percentage label
        self.progress_frame = ttk.Frame(root)
        self.progress_frame.pack(pady=(0,10))
        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", length=250, mode="determinate")
        self.progress.pack(ipady=6)
        self.progress_label = tk.Label(self.progress_frame, text="0%", anchor="center", bg=self.root.cget("bg"))
        self.progress_label.place(relx=0.5, rely=0.5, anchor="center")

#=============== Export Button
        export_btn = ttk.Button(root, text="Export CSV", command=self.export_csv)
        export_btn.pack(pady=10)

#=============== Internal state
        self.results = []
        self.scanning = False
        self.executor = None
        self.animation_running = False
        self.status_ips = []
        self.total_tasks = 0
        self.completed_tasks = 0

#=============== Start scan
    def start_scan(self):
        # basic validation
        try:
            start_port = int(self.start_port.get())
            end_port = int(self.end_port.get())
        except ValueError:
            messagebox.showwarning("Warning", "Ports must be integers")
            return

        self.tree.delete(*self.tree.get_children())
        self.results.clear()
        self.scanning = True
        self.completed_tasks = 0
        self.progress["value"] = 0
        self.progress_label.config(text="0%")

        self.scan_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        start_ip = self.start_ip.get()
        end_ip = self.end_ip.get()
        start_port = start_port
        end_port = end_port

        # quick simple single-octet range handling (expects same base)
        try:
            base = ".".join(start_ip.split(".")[:3])
            start = int(start_ip.split(".")[3])
            end = int(end_ip.split(".")[3])
            ips = [f"{base}.{i}" for i in range(start, end + 1)]
        except Exception:
            messagebox.showwarning("Warning", "IP range must be same base and valid (e.g. 192.168.1.1 -> 192.168.1.10)")
            self.scan_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            return

        self.total_tasks = len(ips) * (end_port - start_port + 1)
        if self.total_tasks <= 0:
            messagebox.showwarning("Warning", "No tasks to perform (check ranges)")
            self.scan_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            return

        self.status_ips = ips[:5]
        self.animation_running = True
        self.animate_status()

        self.executor = ThreadPoolExecutor(max_workers=50)

        def scan_ips():
            for ip in ips:
                if not self.scanning:
                    break
                reachable = ping_host(ip)
                hostname = resolve_hostname(ip) if reachable else "-"
                if reachable:
                    for port in range(start_port, end_port+1):
                        if not self.scanning:
                            break
                        if scan_port(ip, port):
                            self.add_result(ip, hostname, port, "Open")
                        self.completed_tasks += 1
                        self.update_progress(self.completed_tasks / self.total_tasks * 100)
                else:
                    self.add_result(ip, hostname, "-", "Unreachable")
                    self.completed_tasks += (end_port - start_port + 1)
                    self.update_progress(self.completed_tasks / self.total_tasks * 100)

            self.root.after(0, self.scan_complete)

        threading.Thread(target=scan_ips, daemon=True).start()

#=============== Stop scan
    def stop_scan(self):
        self.scanning = False
        self.animation_running = False
        self.status_label.config(text="Scan stopped")
        self.scan_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

#=============== Add result
    def add_result(self, ip, hostname, port, status):
        self.results.append((ip, hostname, port, status))
        self.root.after(0, lambda: self.tree.insert("", "end", values=(ip, hostname, port, status)))

#=============== Scan complete
    def scan_complete(self):
        self.scanning = False
        self.animation_running = False
        self.scan_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="Scan complete")
        self.progress["value"] = 100
        self.progress_label.config(text="100%")

#=============== Animate status
    def animate_status(self):
        if not self.animation_running:
            return
        text_list = []
        for ip in self.status_ips:
            text_list.append(ip + ": " + "."*(((int(time.time()*2))%3)+1))
        self.status_label.config(text="\n".join(text_list))
        self.root.after(500, self.animate_status)

#=============== Update progress
    def update_progress(self, percent):
        # percent: 0..100
        self.progress["value"] = percent
        self.progress_label.config(text=f"{int(percent)}%")

#=============== Export CSV
    def export_csv(self):
        if not self.results:
            messagebox.showwarning("Warning", "No results available!", parent=self.root)
            return
        filename = f"scan_{self.start_ip.get()}-{self.end_ip.get()}_{self.start_port.get()}-{self.end_port.get()}.csv"
        filepath = filedialog.asksaveasfilename(
            parent=self.root,
            defaultextension=".csv",
            initialfile=filename,
            filetypes=[("CSV files", "*.csv")]
        )
        if filepath:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["IP Address", "Hostname", "Port", "Status"])
                for row in self.results:
                    writer.writerow([row[0], row[1], row[2], row[3]])
            messagebox.showinfo("Export", f"Results exported to:\n{filepath}", parent=self.root)


#=============== On close (stop cat and exit)
    def on_close(self):
        # stop the scanner if running
        self.scanning = False
        self.animation_running = False

        # signal cat thread to stop
        try:
            self._cat_stop_event.set()
        except Exception:
            pass

        # small delay to allow thread to clear console (optional)
        time.sleep(0.05)

        # destroy GUI
        try:
            self.root.destroy()
        except Exception:
            pass

#=============== Run App
if __name__ == "__main__":
    root = tk.Tk()
    app = ScannerApp(root)
    root.mainloop()
