# LogON - RFID Technology Based Wifi Enabled Attendance Tracker

##  Overview

This project presents a smart, scalable solution for automating **student attendance tracking** and **mess meal logging** in educational institutions using **RFID technology**. It replaces manual roll calls and meal coupons with a streamlined system where students use RFID cards to register attendance and claim meals. The system integrates hardware (RFID readers, microcontrollers) with a Python-Flask backend and a MySQL database, along with user-friendly web interfaces for teachers and students.

---

##  Features

-  **Subject-wise Attendance Tracking:** Teachers select the subject before class; students scan RFID cards to mark attendance.
-  **Mess Meal Logging:** System logs meals (breakfast/lunch/dinner) based on time when students scan their RFID at mess.
-  **Duplicate Entry Prevention:** Backend prevents double attendance or extra meal claims in the same session.
-  **Web Interface:** - Teachers can start sessions and students can view subject-wise attendance and meal logs.
-  **Centralized Database:** Attendance and meal logs stored in MySQL for analysis and reporting.
-  **Seamless Hardware-Software Integration:** Real-time communication between RFID hardware and backend APIs.

---

##  Technology Stack

###  Hardware
- **RC522 RFID Reader** – For scanning student RFID cards.
- **RFID Cards** – Unique IDs assigned to each student.
- **Arduino Uno / NodeMCU (ESP8266)** – Microcontrollers for interfacing with RFID reader.
- **USB Power Supply / Laptop** – For powering and hosting server.

###  Software
- **Python + Flask** – Backend server and API handling.
- **MySQL** – Database for storing logs and student data.
- **HTML/CSS/JavaScript** – Frontend for web portal.
- **Arduino IDE** – For microcontroller programming.

---

##  Installation

1. **Hardware Setup**
   - Connect RC522 to Arduino/NodeMCU using SPI.
   - Upload Arduino code to microcontroller to read and transmit RFID data.

2. **Backend Setup**
   - Install required Python libraries:
     ```bash
     pip install flask mysql-connector-python
     ```
   - Set up the Flask server and routes for:
     - Starting attendance session
     - Logging attendance and meals
   - Connect backend to MySQL database.

3. **Database Setup**
   - Create tables for:
     - `Students`, `Teachers`, `Subjects`
     - `Active_Sessions`, `RFID_Log`, `Meal_Timings`, `Meal_Logs`
   - Import the schema using MySQL Workbench or command line.

4. **Frontend Setup**
   - Use HTML/CSS to create:
     - Teacher interface (subject selection, session start)
     - Student portal (view logs and attendance %)

---

##  Usage

1. **For Attendance:**
   - Teacher selects subject via web interface and starts session.
   - Students scan RFID card; backend logs ID, subject, timestamp.

2. **For Mess Meal Tracking:**
   - Student scans RFID card at the mess.
   - System auto-categorizes meal based on current time (e.g., lunch).
   - Backend checks for duplicate entries in same meal period.

3. **Student Dashboard:**
   - Enter student ID to view attendance % per subject.
   - See whether 75% attendance criteria are met.

4. **Reporting:**
   - Admins can query database for logs and generate CSV reports.

---

##  Dependencies

- `Python 3.8+`
- `Flask`
- `MySQL`
- `mysql-connector-python`
- `Arduino IDE`
- Browser for frontend (Chrome/Firefox)
