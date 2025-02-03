import sys
import requests
import subprocess
import time
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QMessageBox, QListWidget, QHBoxLayout, QProgressBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, pyqtSignal, QObject

SERVER_URL = "http://127.0.0.1:5000"

sys.stdout.reconfigure(encoding='utf-8')  # Ensure UTF-8 encoding

def is_server_running():
    try:
        response = requests.get("http://127.0.0.1:5000")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

# Determine the correct server path when running as .exe
if getattr(sys, 'frozen', False):
    server_path = os.path.join(sys._MEIPASS, "server.py")
else:
    server_path = os.path.join(os.path.dirname(__file__), "server.py")

log_file = "server_debug.log"  # Log server output

if not is_server_running():
    print("Starting server...")
    try:
        with open(log_file, "w") as log:
            server_process = subprocess.Popen(
                [sys.executable, server_path],
                stdout=log, stderr=log, text=True
            )

        # Wait for server to start
        for i in range(10):
            time.sleep(1)
            if is_server_running():
                print("Server started successfully.")
                break
        else:
            print("Error: Server failed to start.")
            with open(log_file, "r") as log:
                print(log.read())  # Print server logs for debugging
            sys.exit(1)

    except Exception as e:
        print(f" Exception while starting server: {e}")
        sys.exit(1)
else:
    print(" Server is already running.")

print("Launching UI...")

class WorkerSignals(QObject):
    success = pyqtSignal(dict)
    error = pyqtSignal(str)

class APIWorker(QRunnable):
    def __init__(self, endpoint, data=None, signals=None):
        super().__init__()
        self.endpoint = endpoint
        self.data = data
        self.signals = signals

    @pyqtSlot()
    def run(self):
        try:
            if self.data:
                response = requests.post(f"{SERVER_URL}/{self.endpoint}", json=self.data)
            else:
                response = requests.get(f"{SERVER_URL}/{self.endpoint}")
            response_data = response.json()
            if response.status_code == 200:
                self.signals.success.emit(response_data)
            else:
                self.signals.error.emit(response_data.get("error", "Unknown error"))
        except Exception as e:
            self.signals.error.emit(str(e))

class InventoryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Inventory Management")
        self.setGeometry(200, 200, 500, 400)  # Set window size

        layout = QVBoxLayout()

        # Title Label
        self.title_label = QLabel(" Inventory Management System")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(self.title_label)

        # Input Fields
        input_layout = QHBoxLayout()
        self.item_name = QLineEdit(self)
        self.item_name.setPlaceholderText("Enter Item Name")
        self.item_name.setStyleSheet("padding: 6px; border-radius: 5px; border: 1px solid #aaa;")
        
        self.item_quantity = QLineEdit(self)
        self.item_quantity.setPlaceholderText("Enter Quantity")
        self.item_quantity.setStyleSheet("padding: 6px; border-radius: 5px; border: 1px solid #aaa;")

        input_layout.addWidget(self.item_name)
        input_layout.addWidget(self.item_quantity)
        layout.addLayout(input_layout)

        # Buttons with icons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton(QIcon("icons/add.png"), "Add Item", self)
        self.add_btn.clicked.connect(self.add_item)
        btn_layout.addWidget(self.add_btn)

        self.remove_btn = QPushButton(QIcon("icons/remove.png"), "Remove Item", self)
        self.remove_btn.clicked.connect(self.remove_item)
        btn_layout.addWidget(self.remove_btn)

        self.update_btn = QPushButton(QIcon("icons/update.png"), "Update Quantity", self)
        self.update_btn.clicked.connect(self.update_quantity)
        btn_layout.addWidget(self.update_btn)

        layout.addLayout(btn_layout)

        # Inventory List
        self.inventory_list = QListWidget(self)
        layout.addWidget(self.inventory_list)

        # Purchase & Return Buttons
        purchase_return_layout = QHBoxLayout()

        self.purchase_btn = QPushButton(QIcon("icons/cart.png"), "Purchase Item", self)
        self.purchase_btn.clicked.connect(self.purchase_item)
        purchase_return_layout.addWidget(self.purchase_btn)

        self.return_btn = QPushButton(QIcon("icons/return.png"), "Return Item", self)
        self.return_btn.clicked.connect(self.return_item)
        purchase_return_layout.addWidget(self.return_btn)

        layout.addLayout(purchase_return_layout)

        # Refresh Button & Progress Bar
        refresh_layout = QHBoxLayout()

        self.refresh_btn = QPushButton(QIcon("icons/refresh.png"), "Refresh Inventory", self)
        self.refresh_btn.clicked.connect(self.load_inventory)
        refresh_layout.addWidget(self.refresh_btn)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        refresh_layout.addWidget(self.progress_bar)

        layout.addLayout(refresh_layout)

        self.setLayout(layout)
        self.load_inventory()
        self.show()

    def execute_api_request(self, endpoint, data=None, success_callback=None):
        self.progress_bar.setValue(30)  # Show progress
        signals = WorkerSignals()
        if success_callback:
            signals.success.connect(success_callback)
        signals.error.connect(self.show_error)

        worker = APIWorker(endpoint, data, signals)
        self.threadpool.start(worker)
        
        

    def add_item(self):
        name = self.item_name.text().strip()
        quantity = self.item_quantity.text().strip()
        if not name or not quantity:
            QMessageBox.warning(self, "Error", "Both name and quantity are required.")
            return
        try:
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a valid integer.")
            return
        self.execute_api_request("add-item", {"name": name, "quantity": quantity}, self.load_inventory)

    def remove_item(self):
        name = self.item_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Item name is required.")
            return
        self.execute_api_request("remove-item", {"name": name}, self.load_inventory)

    def update_quantity(self):
        name = self.item_name.text().strip()
        quantity = self.item_quantity.text().strip()
        if not name or not quantity:
            QMessageBox.warning(self, "Error", "Both name and new quantity are required.")
            return
        try:
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a valid integer.")
            return
        self.execute_api_request("update-quantity", {"name": name, "new_quantity": quantity}, self.load_inventory)

    def purchase_item(self):
        name = self.item_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Item name is required.")
            return
        self.execute_api_request("purchase-item", {"name": name}, self.load_inventory)

    def return_item(self):
        name = self.item_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Item name is required.")
            return
        self.execute_api_request("return-item", {"name": name}, self.load_inventory)

    def load_inventory(self):
        self.execute_api_request("get-inventory", success_callback=self.update_inventory_list)

    def update_inventory_list(self, data):
        self.inventory_list.clear()
        self.progress_bar.setValue(70)  # Progress halfway

        inventory = data.get("inventory", [])
        if not inventory:
            self.inventory_list.addItem("No items in inventory.")
        else:
            for item in inventory:
                self.inventory_list.addItem(f"{item['name']} - {item['quantity']}")

        self.progress_bar.setValue(100)  # Progress complete
        
        
    def closeEvent(self, event):
        server_process.terminate()  # Kill server on exit
        event.accept()

    def show_error(self, error_msg):
        QMessageBox.warning(self, "Error", error_msg)
        self.progress_bar.setValue(0)  # Reset progress on error

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InventoryApp()
    sys.exit(app.exec_())

