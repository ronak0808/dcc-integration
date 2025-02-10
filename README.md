# dcc-integration
# 🛠️ DCC Integration – Inventory Management App

A Python-based Inventory Management System using **Flask/FastAPI**, **SQLite**, and a **PyQt/PySide GUI**, designed for seamless integration with **Blender/Maya**.

---

## 🚀 Features  
✅ Flask/FastAPI backend for handling inventory data  
✅ SQLite database for efficient data storage  
✅ PyQt/PySide GUI for user-friendly interactions  
✅ REST APIs for smooth integration with external applications  
✅ Supports Blender/Maya scripting  

---
🎯 Running the App (Without Installation)
If you've downloaded this project and just want to run the app:

1️⃣ Navigate to the dist/ folder
2️⃣ Run ui.exe (double-click or use the terminal)

🏗️ Installation & Setup  

1️⃣ Clone the Repository**  

git clone https://github.com/<your-username>/dcc-integration.git
cd dcc-integration

2️⃣ Set Up Virtual Environment
sh
Copy
Edit
# Create a virtual environment
python -m venv venv

# Activate it:
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
3️⃣Install Dependencies
pip install -r requirements.txt


🚦 Running the Project
1️.Start the Backend Server

python server.py
This will start the Flask/FastAPI server at:
🔗 http://127.0.0.1:5000/

2️.Launch the GUI Application

python ui.py

This will open the Inventory Management UI built with PyQt/PySide
