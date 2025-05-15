import sys
import subprocess
import json
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem, QTableWidget, QTabWidget,QTextEdit, QSpinBox, QInputDialog, QFileDialog, QMessageBox, QComboBox, QHBoxLayout, QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QStackedWidget, QMainWindow
from PySide6.QtGui import QFont
import requests

special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '~', '`', '[', '{', ']', '}', '\\', '|', ';', ':', '"', "'", '<', ',', '>', '.', '/', '?']

qemu_path = r"C:\newww\ucrt64\bin\qemu-img.exe"

DARK_BG = "#1e1e1e"
DARK_TEXT = "#ffffff"
ACCENT_BLUE = "#007acc"
ACCENT_CYAN = "#00ffff"
TEXTBOX_BG = "#2d2d2d"
TEXTBOX_FG = "#ffffff"

def gui_log(log_widget, message):
    log_widget.append(message)

def create_dockerfile(save_path, content, log_widget):
    try:
        with open(save_path, "w") as f:
            f.write(content)
        gui_log(log_widget, f"Dockerfile created at {save_path}")
        return True
    except Exception as e:
        gui_log(log_widget, f"Error creating Dockerfile: {e}")
        return False

def build_docker_image(dockerfile_path, image_name, log_widget):
    try:
        subprocess.run(["docker", "build", "-t", image_name, "-f", dockerfile_path, os.path.dirname(dockerfile_path)],
                       check=True, capture_output=True, text=True)
        gui_log(log_widget, f"Image '{image_name}' built.")
        return True
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'docker' command not found. Ensure Docker is installed and running.")
        return False
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error building Docker image: {e.stderr}")
        return False
    except Exception as e:
        gui_log(log_widget, f"An unexpected error occurred: {e}")
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

def search_local_image(image_name, log_widget):
    try:
        output = subprocess.check_output(["docker", "images", image_name], text=True)
        gui_log(log_widget, output)
        return True
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'docker' command not found. Ensure Docker is installed and running.")
        return False
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error searching image '{image_name}': {e.stderr}")
        return False

def list_running_containers(log_widget):
    try:
        output = subprocess.check_output(["docker", "ps"], text=True)
        gui_log(log_widget, "Running Containers:\n" + output)
        return True
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'docker' command not found. Ensure Docker is installed and running.")
        return False
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error listing running containers: {e.stderr}")
        return False

def list_all_containers(log_widget):
    try:
        output = subprocess.check_output(["docker", "ps", "-a"], text=True)
        gui_log(log_widget, "All Containers:\n" + output)
        return True
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'docker' command not found. Ensure Docker is installed and running.")
        return False
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error listing containers: {e.stderr}")
        return False

def stop_container(container_id, log_widget):
    try:
        subprocess.run(["docker", "stop", container_id], check=True, capture_output=True, text=True)
        gui_log(log_widget, f"Container '{container_id}' stopped successfully.")
        return True
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error stopping container '{container_id}': {e.stderr}")
        return False
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'docker' command not found. Ensure Docker is installed and running.")
        return False

def search_dockerhub_image(image_name, output_box, status_label, results_table):
    output_box.clear()
    status_label.setText(f"Searching for '{image_name}'...")
    results_table.setRowCount(0)  
    QApplication.processEvents()  

    try:
        fmt = "{{.Name}}\t{{.Description}}\t{{.StarCount}}\t{{.IsOfficial}}"
        raw_cmd = subprocess.check_output(
            ["docker", "search", "--format", fmt, image_name],
            text=True,
            timeout=10
        )

        if not raw_cmd.strip():
            output_box.append(f"No results found for '{image_name}'. Please check the image name and try again.")
            status_label.setText(f"No results found for '{image_name}'.")
            return

        def truncate(text, max_length):
            return text if len(text) <= max_length else text[:max_length - 3] + "..."

        for line in raw_cmd.splitlines():
            try:
                name, desc, stars, official = line.split("\t")
            except ValueError:
                continue

            desc = desc if desc else "N/A"
            short_desc = truncate(desc, 50)
            official_icon = '✔' if '[OK]' in official else '✗'

            
            stars = f"{int(stars):,}" if stars.isdigit() else stars
            
    
            row_position = results_table.rowCount()
            results_table.insertRow(row_position)
    
    
            results_table.setItem(row_position, 0, QTableWidgetItem(name))
            results_table.setItem(row_position, 1, QTableWidgetItem(short_desc))
    
    
            stars_item = QTableWidgetItem(stars)
            stars_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            results_table.setItem(row_position, 2, stars_item)
    
            results_table.setItem(row_position, 3, QTableWidgetItem(official_icon))



    
            official_item = QTableWidgetItem(official_icon)
            official_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            results_table.setItem(row_position, 3, official_item)



            
            namespace = 'library' if '/' not in name else name.split('/', 1)[0]
            repo = name if '/' not in name else name.split('/', 1)[1]
            api_url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo}/"
            
            try:
                response = requests.get(api_url, timeout=5)
                response.raise_for_status()
                pulls = response.json().get('pull_count', 0)
                pulls = f"{pulls:,}"
            except Exception:
                pulls = 0
                
            
                
            pull_count_item = QTableWidgetItem(str(pulls))
            pull_count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            results_table.setItem(row_position, 4, pull_count_item)


        results_table.setVisible(True)
        
      
        hub_url = f"https://hub.docker.com/r/{image_name}" if '/' in image_name else f"https://hub.docker.com/_/{image_name}"
        output_box.append(f"\n🔗 View on DockerHub: {hub_url}\n")
        status_label.setText(f"Displaying results for '{image_name}'.")

    except subprocess.CalledProcessError as e:
        output_box.append(f"Error searching DockerHub for '{image_name}': {e.stderr}")
        status_label.setText("Error during search.")
    except requests.exceptions.RequestException as e:
        status_label.setText("Error during search.")
        QMessageBox.critical(None, "API Error", f"Could not connect to Docker Hub or an error occurred: {e}")
    except Exception as e:
        status_label.setText("An unexpected error occurred.")
        QMessageBox.critical(None, "Error", f"An unexpected error occurred: {e}")

def pull_docker_image(image_name, log_widget):
    try:
        output = subprocess.check_output(["docker", "pull", image_name], text=True)
        gui_log(log_widget, output)
        return True
    except subprocess.CalledProcessError as e:
        gui_log(log_widget, f"Error pulling image '{image_name}': {e.stderr}")
        return False
    except FileNotFoundError:
        gui_log(log_widget, "Error: 'docker' command not found. Ensure Docker is installed and running.")
        return False

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(700, 200, 800, 600)
        self.setWindowTitle("Cloud Computing")
        self.setStyleSheet("background-color: #4A4A4A; color: white;")
        
        self.layout = QVBoxLayout()
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.create_login_page())  
        self.setLayout(self.layout)
        self.layout.addWidget(self.stacked_widget)

        self.users_file = "users.json"
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as file:
                return json.load(file)
        return {}

    def save_users(self):
        with open(self.users_file, "w") as file:
            json.dump(self.users, file)

    def create_login_page(self):
        login_page = QWidget()
        login_layout = QVBoxLayout()

        login_layout.addSpacing(80)
        
        title_label = QLabel("Welcome to Cloud Management System!")
        title_label.setStyleSheet("color: #F06292;")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(title_label)

        login_layout.addSpacing(80)
        self.username_label = QLabel("Username:")
        self.username_label.setFont(QFont("Arial", 18))
        self.username_input = QLineEdit(self)  
        self.username_input.setFont(QFont("Arial", 16))

        username_layout = QHBoxLayout()
        username_layout.addWidget(self.username_label, alignment=Qt.AlignCenter)
        username_layout.addWidget(self.username_input, alignment=Qt.AlignCenter)

        username_layout.setAlignment(Qt.AlignCenter)
        login_layout.addLayout(username_layout)
        login_layout.addSpacing(30) 
        
        self.password_label = QLabel("Password:")
        self.password_label.setFont(QFont("Arial", 18))
        self.password_input = QLineEdit(self)  
        self.password_input.setEchoMode(QLineEdit.Password)  
        self.password_input.setFont(QFont("Arial", 16))

        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_label,alignment=Qt.AlignCenter)
        password_layout.addWidget(self.password_input,alignment=Qt.AlignCenter)

        password_layout.setAlignment(Qt.AlignCenter)
        login_layout.addLayout(password_layout)
        login_layout.addSpacing(50) 

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("background-color: #D5006D; color: white; font-size: 16px; padding: 10px; border-radius: 8px; width: 180px")
        login_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        self.signup_button = QPushButton("Sign Up")
        self.signup_button.setStyleSheet("background-color: #FFFFFF; color: #D5006D; font-size: 16px; padding: 10px; border-radius: 8px; width: 180px")
        login_layout.addWidget(self.signup_button, alignment=Qt.AlignCenter)

        login_page.setLayout(login_layout)

        self.login_button.clicked.connect(self.login)
        self.signup_button.clicked.connect(self.show_signup_page)

        return login_page

    def create_signup_page(self):
        signup_page = QWidget()
        signup_layout = QVBoxLayout()

        
        signup_username_label = QLabel("Username:")
        signup_username_label.setFont(QFont("Arial", 18))
        signup_username_input = QLineEdit(self)
        signup_username_input.setFont(QFont("Arial", 16))

        signup_layout.addWidget(signup_username_label)
        signup_layout.addWidget(signup_username_input)
        signup_layout.addSpacing(20)

        
        signup_password_label = QLabel("Password:")
        signup_password_label.setFont(QFont("Arial", 18))
        signup_password_input = QLineEdit(self)
        signup_password_input.setEchoMode(QLineEdit.Password)
        signup_password_input.setFont(QFont("Arial", 16))

        signup_layout.addWidget(signup_password_label)
        signup_layout.addWidget(signup_password_input)
        signup_layout.addSpacing(20)

        
        confirm_password_label = QLabel("Confirm Password:")
        confirm_password_label.setFont(QFont("Arial", 18))
        confirm_password_input = QLineEdit(self)
        confirm_password_input.setEchoMode(QLineEdit.Password)
        confirm_password_input.setFont(QFont("Arial", 16))

        signup_layout.addWidget(confirm_password_label)
        signup_layout.addWidget(confirm_password_input)
        signup_layout.addSpacing(30)

        
        signup_action_button = QPushButton("Sign Up")
        signup_action_button.setStyleSheet("background-color: #FFFFFF; color: #E74C3C; font-size: 16px; padding: 10px; border-radius: 8px; width: 180px")
        signup_layout.addWidget(signup_action_button)

        
        backk_button = QPushButton("Back")
        backk_button.setStyleSheet("background-color: #E74C3C; color: white; font-size: 16px; padding: 10px; border-radius: 8px; width: 180px")
        backk_button.clicked.connect(self.show_login_form)
        signup_layout.addWidget(backk_button)

        signup_page.setLayout(signup_layout)


        signup_action_button.clicked.connect(lambda: self.handle_signup(signup_username_input, signup_password_input, confirm_password_input))

        

        return signup_page

    def show_signup_page(self):
        signup_page = self.create_signup_page()
        self.stacked_widget.addWidget(signup_page)
        self.stacked_widget.setCurrentWidget(signup_page)  

    def show_login_form(self):
        self.stacked_widget.setCurrentIndex(0)  

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username in self.users and self.users[username] == password:
            print(f"Welcome {username}!")
            self.main_window = CloudManagementWindow(username)
            self.main_window.show()
            self.close()  
        else:
            print("Invalid username or password")
            QMessageBox.critical(self, "Login Failed", "Invalid username or password", QMessageBox.Ok)

    def handle_signup(self, signup_username_input, signup_password_input, confirm_password_input):
        username = signup_username_input.text()
        password = signup_password_input.text()
        confirm_password = confirm_password_input.text()

        if not username or not password or not confirm_password:
            print("All fields are required!")
            QMessageBox.critical(self, "Sign-Up Failed", "All fields are required. Please fill in all fields.", QMessageBox.Ok)
            return  
    
        if password != confirm_password:
            print("Passwords do not match!")
            QMessageBox.critical(self, "Sign-Up Failed", "Passwords do not match!", QMessageBox.Ok)
        elif len(password) < 8 or not any(char.isdigit() for char in password) or not any(char in "!@#$%^&*()_+" for char in password):
            print("Password must be at least 8 characters long, contain a number, and a special character!")
            QMessageBox.critical(self, "Weak Password", "Password must be at least 8 characters long, contain a number, and a special character like @, #, $, etc.", QMessageBox.Ok)
            
        elif username in self.users:
            print("Username already exists!")
            QMessageBox.critical(self, "Sign-Up Failed", "Username already exists!", QMessageBox.Ok)
        else:
            self.users[username] = password
            self.save_users()
            print("Sign-up successful!")
            QMessageBox.information(self, "Sign-Up Successful", "You have successfully signed up!\nYou will now return to the login page.", QMessageBox.Ok)

            self.show_login_form()
            
class CloudManagementWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Cloud Computing")
        self.setGeometry(700, 200, 800, 600)
        self.setStyleSheet("background-color: #4A4A4A; color: white;")
        self.initUI()

    def initUI(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.start_menu_page = QWidget()
        self.project_page = QWidget()
        self.open_vm_page = QWidget()
        self.open_vd_page = QWidget()
        self.docker_page = self.DockerWidget()

        self.init_start_menu_page()
        self.init_project_page()
        self.open_virtual_machine()
        self.add_virtual_disk()

        self.central_widget.addWidget(self.start_menu_page)
        self.central_widget.addWidget(self.project_page)
        self.central_widget.addWidget(self.open_vm_page)
        self.central_widget.addWidget(self.open_vd_page)
        self.central_widget.addWidget(self.docker_page)

        self.central_widget.setCurrentWidget(self.start_menu_page)

    def init_start_menu_page(self):
        layout = QVBoxLayout()
        
        title_label = QLabel(f"Welcome {self.username}!")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        btn_start = QPushButton("Start")
        btn_start.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_start.clicked.connect(self.start_project)
        layout.addWidget(btn_start)

        btn_exit = QPushButton("Exit")
        btn_exit.setStyleSheet("background-color: #E74C3C; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_exit.clicked.connect(self.close)
        layout.addWidget(btn_exit)

        self.start_menu_page.setLayout(layout)
        self.start_menu_page.show()  

    def init_project_page(self):
        layout = QVBoxLayout()

        btn_add_disk = QPushButton("Create Virtual Disk")
        btn_add_disk.setStyleSheet("background-color: #27AE60; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_add_disk.clicked.connect(self.add_virtual_disk_page)
        layout.addWidget(btn_add_disk)

        btn_open_vm = QPushButton("Create Virtual Machine")
        btn_open_vm.setStyleSheet("background-color: #27AE60; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_open_vm.clicked.connect(self.open_virtual_machine_page)
        layout.addWidget(btn_open_vm)
        
        btn_open_docker = QPushButton("Docker")
        btn_open_docker.setStyleSheet("background-color: #27AE60; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_open_docker.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.docker_page))
        layout.addWidget(btn_open_docker)

        btn_back = QPushButton("Back")
        btn_back.setStyleSheet("background-color: #E74C3C; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_back.clicked.connect(lambda: self.central_widget.setCurrentWidget(self.start_menu_page))
        layout.addWidget(btn_back)

        self.project_page.setLayout(layout)

    def add_virtual_disk(self):
        layout = QVBoxLayout()

    
        allocation_label = QLabel("Disk Allocation Type:")
        allocation_label.setFont(QFont("Arial", 14))
        self.allocation_input = QComboBox()
        self.allocation_input.addItems(["Dynamic", "Fixed"])
        self.allocation_input.setFont(QFont("Arial", 14))
        allocation_layout = QHBoxLayout()
        allocation_layout.addWidget(allocation_label)
        allocation_layout.addWidget(self.allocation_input, stretch=1)
        layout.addLayout(allocation_layout)

        layout.addSpacing(50)


        disk_type_label = QLabel("Disk Format:")
        disk_type_label.setFont(QFont("Arial", 14))
        self.disk_type_input = QComboBox()
        self.disk_type_input.addItems(['vmdk', 'vdi', 'vhd', 'vhdx', 'qcow', 'qcow2', 'raw', 'img'])
        self.disk_type_input.setFont(QFont("Arial", 14))
        disk_type_layout = QHBoxLayout()
        disk_type_layout.addWidget(disk_type_label)
        disk_type_layout.addWidget(self.disk_type_input, stretch=1)


        layout.addLayout(disk_type_layout)

        layout.addSpacing(50)
        
        disk_label = QLabel("Virtual Disk Size (e.g., 10G):")
        disk_label.setFont(QFont("Arial", 14))
        self.disk_input = QLineEdit()
        self.disk_input.setFont(QFont("Arial", 14))


        disk_layout = QHBoxLayout()
        disk_layout.addWidget(disk_label)
        disk_layout.addWidget(self.disk_input, stretch=1)


        layout.addLayout(disk_layout)


        layout.addSpacing(50)  


    
        location_label = QLabel("Location:")
        location_label.setFont(QFont("Arial", 14))
        self.selected_path_edit = QLineEdit()
        self.selected_path_edit.setFont(QFont("Arial", 14))
        path_button = QPushButton("Select Path")
        path_button.setFont(QFont("Arial", 14))
        path_button.setStyleSheet("background-color: #008080; color: white; font-size: 16px; padding: 8px; border-radius: 8px;")
        path_button.clicked.connect(self.select_file_path)


        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(location_label)
        file_path_layout.addWidget(self.selected_path_edit)
        
        file_path_layout.addWidget(path_button)
        layout.addLayout(file_path_layout)

        layout.addSpacing(55)

    
        btn_create = QPushButton("Create Virtual Disk")
        btn_create.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_create.clicked.connect(self.create_virtual_disk)
        layout.addWidget(btn_create)

    
        btn_resize = QPushButton("Resize Virtual Disk")
        btn_resize.setStyleSheet("background-color: #27AE60; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_resize.clicked.connect(self.resize_virtual_disk)
        layout.addWidget(btn_resize)

    
        btn_back = QPushButton("Back")
        btn_back.setStyleSheet("background-color: #E74C3C; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_back.clicked.connect(self.start_project)
        layout.addWidget(btn_back)

        self.open_vd_page.setLayout(layout)
        self.selected_path = ""

    def select_file_path(self):
        options = QFileDialog.Options()
        disk_type = self.disk_type_input.currentText()
        default_filter = f"{disk_type.upper()} Files (*.{disk_type});;All Files (*)"
        path, _ = QFileDialog.getSaveFileName(
            self, "Location", f"untitled.{disk_type}", default_filter, options=options
        )

        if path:
            if not path.lower().endswith(f".{disk_type}"):
                path += f".{disk_type}"
            self.selected_path = path
            self.selected_path_edit.setText(self.selected_path)
        else:
            self.selected_path = ""
            self.selected_path_label.setText("No disk file selected.")

    def resize_virtual_disk(self):
        layout = QVBoxLayout()

        disk_label = QLabel("Resize Virtual Disk")
        disk_label.setFont(QFont("Arial", 14))
        layout.addWidget(disk_label)

        self.resize_disk_path = QLineEdit()
        self.resize_disk_path.setFont(QFont("Arial", 14)) 
        disk_browse_btn = QPushButton("Browse...")
        disk_browse_btn.setFont(QFont("Arial", 14))
        disk_browse_btn.clicked.connect(self.resize_virtual_disk)
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(self.resize_disk_path)
        disk_layout.addWidget(disk_browse_btn)
        layout.addLayout(disk_layout)

        if not self.selected_path or not os.path.exists(self.selected_path):
            QMessageBox.critical(self, "Error", "Please select an existing virtual disk.")
            return

        new_size, ok = QInputDialog.getText(
            self, "Resize Disk", "Enter new size (e.g., 10G)")
        if not ok or not new_size.strip():
            return

        self.disk_input.setText(new_size.strip())
        
        
        try:
            result = subprocess.run(
                [qemu_path, 'info', '--output=json', self.selected_path],
                check=True, stdout=subprocess.PIPE, text=True)
            info = json.loads(result.stdout)
            current_virtual_size = int(info['virtual-size'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read current disk size:\n{e}")
            return

        unit = new_size[-1].upper()
        number = float(new_size[:-1])
        new_size_bytes = {'G': 1024**3, 'M': 1024**2, 'T': 1024**4}.get(unit, 0) * number

        if new_size_bytes < current_virtual_size:
            QMessageBox.critical(self, "Error",
                                 "Shrinking disks is not supported by QEMU. Only expansion is allowed.")
            return

        command = [qemu_path, 'resize', self.selected_path, new_size]

        try:
            subprocess.run(command, check=True)
            QMessageBox.information(self, "Success", f"Disk resized to {new_size} successfully!")
            
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to resize disk:\n{e}")

    def create_virtual_disk(self):
        disk_size = self.disk_input.text().strip()
        disk_type = self.disk_type_input.currentText()

        if not disk_size or not disk_type or not self.selected_path:
            QMessageBox.critical(self, "Error", "All fields are required.")
            return

        if not os.path.exists(qemu_path):
            QMessageBox.critical(self, "Error", f"QEMU not found at {qemu_path}.")
            return

        if not any(unit in disk_size for unit in ['G', 'T', 'M']):
            QMessageBox.critical(self, "Error", "Size must include unit (G, M, T).")
            return

        if any(char in disk_size for char in special_chars):
            QMessageBox.critical(self, 'Error', 'Size cannot contain special characters!')
            return
        
        if disk_type.lower() == 'img':
            disk_type = 'raw'
            if not self.selected_path.endswith('.img'):
                self.selected_path += '.img'

        command = [qemu_path, 'create', '-f', disk_type]
        
        if self.allocation_input.currentText() == "Fixed":
            if not disk_type in ['vmdk', 'vdi', 'vhd', 'vhdx', 'qcow', 'qcow2', 'raw']:
                command += ['-o', 'preallocation=full']
        
        command += [self.selected_path, disk_size]

        try:
            subprocess.run(command, check=True)
            QMessageBox.information(self, "Success", "Virtual disk created successfully!")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to create disk:\n{e}")

    def open_virtual_machine(self):
        layout = QVBoxLayout()

        self.vm_name = QLineEdit()
        vm_name_label = QLabel("Virtual machine name:")
        vm_name_label.setFont(QFont("Arial", 14))
        self.vm_name.setFont(QFont("Arial", 14))
        layout.addWidget(vm_name_label)
        layout.addWidget(self.vm_name)

        cpu_label = QLabel("CPU:")
        cpu_label.setFont(QFont("Arial", 14))
        layout.addWidget(cpu_label)

        self.cpu_cores = QSpinBox()
        self.cpu_cores.setRange(1, 4)
        self.cpu_cores.setFont(QFont("Arial", 14))
        layout.addWidget(self.cpu_cores)

        memory_label = QLabel("Memory (MB):")
        memory_label.setFont(QFont("Arial", 14))
        layout.addWidget(memory_label)

        self.memory = QSpinBox()
        self.memory.setRange(512, 32768)
        self.memory.setValue(4096)
        self.memory.setFont(QFont("Arial", 14))
        layout.addWidget(self.memory)

        
        disk_label = QLabel('Add Virtual Disk:')
        disk_label.setFont(QFont("Arial", 14))
        layout.addWidget(disk_label)

        self.disk_path = QLineEdit()
        self.disk_path.setFont(QFont("Arial", 14))  
        disk_browse_btn = QPushButton("Browse...")
        disk_browse_btn.setFont(QFont("Arial", 14))
        disk_browse_btn.clicked.connect(self.browse_virtual_disk)
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(self.disk_path)
        disk_layout.addWidget(disk_browse_btn)
        disk_browse_btn.setStyleSheet("background-color: #008080; color: white; font-size: 16px; padding: 8px; border-radius: 8px;")
        layout.addLayout(disk_layout)

        
        iso_label = QLabel('ISO File Path:')
        iso_label.setFont(QFont("Arial", 14))
        layout.addWidget(iso_label)

        self.iso_path = QLineEdit()
        self.iso_path.setFont(QFont("Arial", 14))
        iso_btn = QPushButton('Browse...')
        iso_btn.setFont(QFont("Arial", 14))
        iso_btn.clicked.connect(self.browse_iso)
        iso_layout = QHBoxLayout()
        iso_layout.addWidget(self.iso_path)
        iso_layout.addWidget(iso_btn)
        iso_btn.setStyleSheet("background-color: #008080; color: white; font-size: 16px; padding: 8px; border-radius: 8px;")
        layout.addLayout(iso_layout)

        btn_create = QPushButton("Open Virtual Machine")
        btn_create.setFont(QFont("Arial", 14))
        btn_create.setStyleSheet("background-color: #1E90FF; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_create.clicked.connect(self.create_vm)
        layout.addWidget(btn_create)

        btn_back = QPushButton("Back")
        btn_back.setFont(QFont("Arial", 14))
        btn_back.setStyleSheet("background-color: #E74C3C; color: white; font-size: 16px; padding: 10px; border-radius: 8px;")
        btn_back.clicked.connect(self.start_project)
        layout.addWidget(btn_back)

        self.open_vm_page.setLayout(layout)
        
    def create_vm(self):
        if not self.vm_name.text().strip():
            QMessageBox.critical(self, 'Error', 'VM name is required!')
            return
        if self.vm_name.text()[0].isdigit():
            QMessageBox.critical(self, 'Error', 'VM name cannot start with a number!')
            return
        if any(char in self.vm_name.text() for char in special_chars):
            QMessageBox.critical(self, 'Error', 'VM name cannot contain special characters like @, &, #, ?, etc.')
            return
        if not self.cpu_cores.value():
            QMessageBox.critical(self, 'Error', 'CPU is required!')
            return
        if not self.memory.value() and not (self.memory.value() > 512 and self.memory.value() < 32768):
            QMessageBox.critical(self, 'Error', 'Memory must be between 512 and 32768 MB!')
            return
        if not self.iso_path.text().strip():
            QMessageBox.critical(self, 'Error', 'ISO Path is required!')
            return
        if not self.disk_path.text().strip():
            QMessageBox.critical(self, 'Error', 'Virtual Disk Path is required!')
            return

        disk_path_str = self.disk_path.text().strip()
        ext = os.path.splitext(disk_path_str)[1].lower().lstrip('.')
        valid_extensions = [self.disk_type_input.itemText(i) for i in range(self.disk_type_input.count())]
        if ext not in valid_extensions:
            QMessageBox.critical(self, 'Error', f'Invalid disk format! Allowed: {", ".join(valid_extensions)}')
            return

        config = {
            'name': self.vm_name.text(),
            'cpu': self.cpu_cores.value(),
            'memory': self.memory.value(),
            'disk': self.disk_path.text(),
            'iso': self.iso_path.text()
        }

        try:
            subprocess.Popen([
                r"c:\newww\ucrt64\bin\qemu-system-x86_64.exe",
                "-m", str(config['memory']),
                "-cpu", "max",
                "-smp", str(config['cpu']),
                "-hda", str(config['disk']),
                "-cdrom", str(config['iso']),
                "-boot", "menu=on",
                "-display", "sdl"
            ])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch VM:\n{e}")

    def browse_iso(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select ISO', '', 'ISO Files (*.iso)')
        if path:
            self.iso_path.setText(path)

    def browse_virtual_disk(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Add Virtual Disk',
                                              '', 'Disk Files (*.qcow2 *.raw *.vmdk *.img *.vdi *.vhd *.vhdx);;All Files (*)')
        if path:
            self.disk_path.setText(path)

    def open_virtual_machine_page(self):
        self.central_widget.setCurrentWidget(self.open_vm_page)

    def add_virtual_disk_page(self):
        self.central_widget.setCurrentWidget(self.open_vd_page)

    def start_project(self):
        self.central_widget.setCurrentWidget(self.project_page)
        self.vm_name.clear()
        self.cpu_cores.setValue(1)
        self.memory.setValue(4096)
        self.disk_path.clear()
        self.iso_path.clear()
        self.allocation_input.setCurrentIndex(0)          
        self.disk_type_input.setCurrentIndex(0)           
        self.disk_input.clear()                           
        self.selected_path_edit.clear()                  
        self.selected_path = ""                       

    class DockerWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.setStyleSheet(f"""
                QWidget {{ background-color: {DARK_BG}; color: {DARK_TEXT}; }}
                QTextEdit {{ background-color: {TEXTBOX_BG}; color: {TEXTBOX_FG}; }}
                QPushButton {{ background-color: {ACCENT_BLUE}; color: {DARK_TEXT}; }}
                QPushButton:hover {{ background-color: {ACCENT_CYAN}; }}
            """)

            self.status_label = QLabel("Ready")
            self.status_label.setAlignment(Qt.AlignCenter)
            self.status_label.setVisible(False)
            self.tabs = QTabWidget()
            self.tabs.setStyleSheet("""
                QTabWidget::pane { border: 0; }
                QTabBar::tab {
                background: #ffffff;
                color: black;
                padding: 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                background: #dddddd;
                }
                """)
        

            self.results_table = QTableWidget()
            self.results_table.setColumnCount(5) 
            self.results_table.setHorizontalHeaderLabels(['Name', 'Description', 'Stars', 'Official', 'Pull Count'])
            self.results_table.setColumnWidth(0, 100)
            self.results_table.setColumnWidth(1, 200)
            self.results_table.setColumnWidth(2, 100)
            self.results_table.setColumnWidth(3, 100)
            self.results_table.setColumnWidth(4, 150)
            for row in range(self.results_table.rowCount()):
                for column in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, column)
                    if item is not None:
                        item.setTextAlignment(Qt.AlignCenter)
            self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.results_table.setSelectionMode(QAbstractItemView.NoSelection)
            self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.results_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.results_table.setStyleSheet("""
                QHeaderView::section {
                background-color: #d3d3d3;  /* Light grey background for header */
                color: black;  /* Black text color for header */
                font-weight: bold;  /* Bold header text */
                }
                QTableWidget::item {
                background-color: #e0e0e0;  /* Grey background for data cells */
                color: black;  /* <-- Add this line for font color */
                }
                QTableWidget::item:even {
                background-color: #f5f5f5;  /* Lighter grey for even rows */
                }
                QTableWidget::item:odd {
                background-color: #e0e0e0;  /* Darker grey for odd rows */
                }
        """)
            self.results_table.setVisible(False)           
            
            self.output_box = QTextEdit()
            self.output_box.setReadOnly(True)
            
            self.init_docker_tab()

            layout = QVBoxLayout()
            layout.addWidget(self.tabs)
            layout.addWidget(self.status_label) 
            layout.addWidget(self.results_table)
            layout.addWidget(self.output_box)
            self.setLayout(layout)

        def init_docker_tab(self):
            docker_tab = QWidget()
            self.tabs.addTab(docker_tab, "Docker")
            layout = QVBoxLayout()  

            self.dockerfile_text = QTextEdit()
            layout.addWidget(self.dockerfile_text)

            create_btn = QPushButton("Create Dockerfile")
            build_btn = QPushButton("Build Docker Image")
            list_btn = QPushButton("List Images")
            search_btn = QPushButton("Search Image")
            list_running_btn = QPushButton("List all Running Containers")
            list_all_btn = QPushButton("List All Containers")
            stop_btn = QPushButton("Stop Container")
            search_hub_btn = QPushButton("Search DockerHub")
            pull_btn = QPushButton("Pull Image")
            
            create_btn.clicked.connect(self.create_dockerfile_action)
            build_btn.clicked.connect(self.build_image_action)
            list_btn.clicked.connect(self.list_images_action)
            search_btn.clicked.connect(self.search_image_action)
            list_running_btn.clicked.connect(self.list_running_containers_action)
            list_all_btn.clicked.connect(self.list_all_containers_action) 
            stop_btn.clicked.connect(self.stop_container_action)
            search_hub_btn.clicked.connect(self.search_dockerhub_action)
            pull_btn.clicked.connect(self.pull_image_action)

            top_row = QHBoxLayout()
            for btn in [create_btn, build_btn, list_btn, search_btn]:
                top_row.addWidget(btn)

            bottom_row = QHBoxLayout()
            for btn in [list_running_btn, list_all_btn, stop_btn, search_hub_btn, pull_btn]:
                bottom_row.addWidget(btn)
                
            layout.addLayout(top_row)
            layout.addLayout(bottom_row)

            docker_tab.setLayout(layout)
            self.tabs.addTab(docker_tab, "Docker")

        def create_dockerfile_action(self):
            path, _ = QFileDialog.getSaveFileName(self, "Save Dockerfile", filter="Dockerfile (*)")
            if path:
                content = self.dockerfile_text.toPlainText()
                create_dockerfile(path, content, self.output_box)

        def build_image_action(self):
            dockerfile_path, _ = QFileDialog.getOpenFileName(self, "Select Dockerfile")
            if dockerfile_path:
                image_name, ok = QInputDialog.getText(self, "Image Name", "Enter image name:")
                if ok and image_name:
                    build_docker_image(dockerfile_path, image_name, self.output_box)

        def list_images_action(self):
            list_docker_images(self.output_box)

        def search_image_action(self):
            image_name, ok = QInputDialog.getText(self, "Search Image", "Enter image name:")
            if ok and image_name:
                search_local_image(image_name, self.output_box)
                
                
        def list_running_containers_action(self):
            list_running_containers(self.output_box)

        def list_all_containers_action(self):
            list_all_containers(self.output_box)
            
        def stop_container_action(self):
            container_id, ok = QInputDialog.getText(self, "Stop Container", "Enter container ID or name:")
            if ok and container_id:
                stop_container(container_id.strip(), self.output_box)

        def search_dockerhub_action(self):
            image_name, ok = QInputDialog.getText(self, "Search DockerHub", "Enter image name:")
            if ok and image_name:
                self.status_label.setVisible(True)
                search_dockerhub_image(image_name.strip(), self.output_box, self.status_label, self.results_table)
                self.results_table.setVisible(True)
                self.results_table.clearContents()
                self.results_table.setRowCount(0)
                self.output_box.clear()
                search_dockerhub_image(
                    image_name.strip(),
                    self.output_box,
                    self.status_label,
                    self.results_table
                )

        def pull_image_action(self):
            image_name, ok = QInputDialog.getText(self, "Pull Image", "Enter image name to download:")
            if ok and image_name:
                pull_docker_image(image_name.strip(), self.output_box)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
