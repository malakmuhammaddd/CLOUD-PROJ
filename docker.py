import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

DEFAULT_ISO_PATH = r"D:\\4\\cloud\\ubuntu-24.04.2-desktop-amd64.iso"

DARK_BG = "#1e1e1e"
DARK_TEXT = "#ffffff"
ACCENT_BLUE = "#007acc"
ACCENT_CYAN = "#00ffff"
TEXTBOX_BG = "#2d2d2d"
TEXTBOX_FG = "#ffffff"

def validate_size(size_str):
    if not any(size_str.endswith(unit) for unit in ['G', 'M', 'K']) or not size_str[:-1].isdigit():
        raise ValueError("Invalid size format. Use numbers followed by 'G', 'M', or 'K' (e.g., 10G, 500M).")
    return size_str

def validate_int_input(value_str, field_name):
    if not value_str.isdigit():
        raise ValueError(f"Invalid {field_name}. Please enter a whole number.")
    return value_str

def create_dockerfile(save_path, content, log_widget):
    try:
        with open(save_path, "w") as f:
            f.write(content)
        message = f"Dockerfile created at {save_path}"
        gui_log(log_widget, message)
        return True
    except Exception as e:
        gui_log(log_widget, f"Error creating Dockerfile: {e}")
        return False

def build_docker_image(dockerfile_path, image_name, log_widget):
    try:
        subprocess.run(["docker", "build", "-t", image_name, "-f", dockerfile_path, os.path.dirname(dockerfile_path)], check=True, capture_output=True, text=True)
        message = f"Image '{image_name}' built."
        gui_log(log_widget, message)
        return True
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'docker' command not found. Ensure Docker is installed and running.")
        return False
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error building Docker image: {e.stderr}")
        return False
    except Exception as e:
        gui_log(log_widget, f"An unexpected error occurred during Docker image build: {e}")
        return False

def list_docker_images(log_widget):
    try:
        output = subprocess.check_output(["docker", "images"], text=True)
        gui_log(log_widget, output)
        return True
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'docker' command not found. Ensure Docker is installed and running.")
        return False
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error listing Docker images: {e.stderr}")
        return False
    except Exception as e:
        gui_log(log_widget, f"An unexpected error occurred while listing Docker images: {e}")
        return False

def search_local_image(image_name, log_widget):
    try:
        output = subprocess.check_output(["docker", "images", image_name], text=True)
        gui_log(log_widget, output)
        return True
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'docker' command not found. Ensure Docker is installed and running.")
        return False
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error searching for local image '{image_name}': {e.stderr}")
        return False
    except Exception as e:
        gui_log(log_widget, f"An unexpected error occurred while searching for local image '{image_name}': {e}")
        return False

def gui_log(log_widget, message):
    log_widget.insert(tk.END, message + "\n")
    log_widget.see(tk.END)

def main_gui():
    root = tk.Tk()
    root.title("Cloud Management System")
    root.configure(bg=DARK_BG)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background=DARK_BG)
    style.configure("TLabel", background=DARK_BG, foreground=DARK_TEXT)
    style.configure("TButton", background=ACCENT_BLUE, foreground=DARK_TEXT)
    style.map("TButton", background=[('active', ACCENT_CYAN)])

    tab_control = ttk.Notebook(root)
    docker_tab = ttk.Frame(tab_control)
    tab_control.add(docker_tab, text='Docker')

    dockerfile_content = tk.Text(docker_tab, height=10, width=50, bg=TEXTBOX_BG, fg=TEXTBOX_FG, insertbackground=DARK_TEXT)
    dockerfile_content.grid(row=0, column=0, columnspan=3, padx=10, pady=5)

    ttk.Button(docker_tab, text="Create Dockerfile", command=lambda: create_dockerfile(
        filedialog.asksaveasfilename(defaultextension="Dockerfile"), dockerfile_content.get("1.0", tk.END), output_box)).grid(row=1, column=0, pady=5)

    ttk.Button(docker_tab, text="Build Docker Image", command=lambda: build_docker_image(
        filedialog.askopenfilename(title="Select Dockerfile"), simple_input_popup("Image Name/Tag"), output_box)).grid(row=1, column=1, pady=5)

    ttk.Button(docker_tab, text="List Images", command=lambda: list_docker_images(output_box)).grid(row=2, column=0, pady=5)
    ttk.Button(docker_tab, text="Search Image", command=lambda: search_local_image(simple_input_popup("Local Image Name"), output_box)).grid(row=3, column=0, pady=5)

    output_box = scrolledtext.ScrolledText(root, height=15, width=100, bg=TEXTBOX_BG, fg=TEXTBOX_FG, insertbackground=DARK_TEXT)
    output_box.pack(fill="both", expand=True, padx=10, pady=5)

    tab_control.pack(expand=1, fill="both", padx=10, pady=5)
    root.mainloop()

def simple_input_popup(prompt):
    win = tk.Toplevel(bg=DARK_BG)
    win.title(prompt)
    tk.Label(win, text=prompt, bg=DARK_BG, fg=DARK_TEXT).pack()
    entry = tk.Entry(win, bg=TEXTBOX_BG, fg=TEXTBOX_FG, insertbackground=DARK_TEXT)
    entry.pack()
    result = []
    def on_ok():
        result.append(entry.get())
        win.destroy()
    tk.Button(win, text="OK", bg=ACCENT_BLUE, fg=DARK_TEXT, command=on_ok).pack()
    win.wait_window()
    return result[0] if result else ""

if __name__ == '__main__':
    main_gui()
