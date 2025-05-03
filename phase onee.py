import sys
import subprocess
import json
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import  QSpinBox, QInputDialog, QFileDialog, QMessageBox, QComboBox, QHBoxLayout, QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QStackedWidget, QMainWindow
from PySide6.QtGui import QFont

special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '~', '`', '[', '{', ']', '}', '\\', '|', ';', ':', '"', "'", '<', ',', '>', '.', '/', '?']

qemu_path = r"C:\newww\ucrt64\bin\qemu-img.exe"


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(700, 200, 800, 600)
        self.setWindowTitle("Cloud Computing")
        self.setStyleSheet("background-color: #4A4A4A; color: white;")
        
        self.layout = QVBoxLayout()

        # Create a stacked widget to hold the login and sign-up pages
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.create_login_page())  # Add login page as the first page
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
        # Title label
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

        # Create username label and input
        signup_username_label = QLabel("Username:")
        signup_username_label.setFont(QFont("Arial", 18))
        signup_username_input = QLineEdit(self)
        signup_username_input.setFont(QFont("Arial", 16))

        signup_layout.addWidget(signup_username_label)
        signup_layout.addWidget(signup_username_input)
        signup_layout.addSpacing(20)

        # Create password label and input
        signup_password_label = QLabel("Password:")
        signup_password_label.setFont(QFont("Arial", 18))
        signup_password_input = QLineEdit(self)
        signup_password_input.setEchoMode(QLineEdit.Password)
        signup_password_input.setFont(QFont("Arial", 16))

        signup_layout.addWidget(signup_password_label)
        signup_layout.addWidget(signup_password_input)
        signup_layout.addSpacing(20)

        # Create confirm password label and input
        confirm_password_label = QLabel("Confirm Password:")
        confirm_password_label.setFont(QFont("Arial", 18))
        confirm_password_input = QLineEdit(self)
        confirm_password_input.setEchoMode(QLineEdit.Password)
        confirm_password_input.setFont(QFont("Arial", 16))

        signup_layout.addWidget(confirm_password_label)
        signup_layout.addWidget(confirm_password_input)
        signup_layout.addSpacing(30)

        # Create sign-up button
        signup_action_button = QPushButton("Sign Up")
        signup_action_button.setStyleSheet("background-color: #FFFFFF; color: #E74C3C; font-size: 16px; padding: 10px; border-radius: 8px; width: 180px")
        signup_layout.addWidget(signup_action_button)

        # Create cancel button to return to login form
        backk_button = QPushButton("Back")
        backk_button.setStyleSheet("background-color: #E74C3C; color: white; font-size: 16px; padding: 10px; border-radius: 8px; width: 180px")
        backk_button.clicked.connect(self.show_login_form)
        signup_layout.addWidget(backk_button)

        signup_page.setLayout(signup_layout)


        signup_action_button.clicked.connect(lambda: self.handle_signup(signup_username_input, signup_password_input, confirm_password_input))

        

        return signup_page

    def show_signup_page(self):
        # Create the signup page and add it to the stacked widget
        signup_page = self.create_signup_page()
        self.stacked_widget.addWidget(signup_page)
        self.stacked_widget.setCurrentWidget(signup_page)  # Switch to sign-up page

    def show_login_form(self):
        self.stacked_widget.setCurrentIndex(0)  # Index 0 is your login page

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username in self.users and self.users[username] == password:
            print(f"Welcome {username}!")
            # Handle successful login, show main window
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

    # Basic validation for password match
        if not username or not password or not confirm_password:
            print("All fields are required!")
            QMessageBox.critical(self, "Sign-Up Failed", "All fields are required. Please fill in all fields.", QMessageBox.Ok)
            return  # Exit the function if any field is empty
    
        if password != confirm_password:
            print("Passwords do not match!")
            QMessageBox.critical(self, "Sign-Up Failed", "Passwords do not match!", QMessageBox.Ok)
    # Check if the password is weak (less than 8 characters, no number, and no special character)
        elif len(password) < 8 or not any(char.isdigit() for char in password) or not any(char in "!@#$%^&*()_+" for char in password):
            print("Password must be at least 8 characters long, contain a number, and a special character!")
            QMessageBox.critical(self, "Weak Password", "Password must be at least 8 characters long, contain a number, and a special character like @, #, $, etc.", QMessageBox.Ok)
    # Check if the username already exists
        elif username in self.users:
            print("Username already exists!")
            QMessageBox.critical(self, "Sign-Up Failed", "Username already exists!", QMessageBox.Ok)
        else:
        # Add the new user to the users dictionary
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

        self.init_start_menu_page()
        self.init_project_page()
        self.open_virtual_machine()
        self.add_virtual_disk()

        self.central_widget.addWidget(self.start_menu_page)
        self.central_widget.addWidget(self.project_page)
        self.central_widget.addWidget(self.open_vm_page)
        self.central_widget.addWidget(self.open_vd_page)

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

        
        self.vm_name.clear()
        self.cpu_cores.setValue(1)
        self.memory.setValue(4096)
        self.disk_path.clear()
        self.iso_path.clear()


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())
