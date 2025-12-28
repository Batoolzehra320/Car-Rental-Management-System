
# 🚗 Car Rental Management System 

A desktop-based Car Rental Management System built using **Python** and **Tkinter** for GUI, and **CSV files** for storage. The system supports car rentals, returns, balance management, and administrative control via a simple desktop interface.
---

## 📌 Key Features

### 👤 Customer Functions
- User registration and login
- View available cars for rent
- Rent cars with multiple payment options
- Return cars (includes late fee calculation)
- View rental history
- Submit feedback on rented cars

### 🔧 Admin Functions
- Login with fixed credentials (admin/admin123)
- Add or remove cars
- View all rentals and reserved cars
- Review customer feedback
- Set or update admin rental balance
- View current admin balance

---

## 
- **Abstract Base Class (`CSVStorable`)** to enforce `save_to_csv()` across entities.
- **Fixed Admin Login** with balance tracking and management.
- **Better Validation** in forms and data input (e.g., balance, card details).
- **Improved GUI** with scrollable feedback, rental lists, and admin controls.
- **Rental Duration Tracking** and total cost calculation based on days.
- **Cleaner Code Organization** with comments and modular methods.

---

## Technologies Used

- Python 3
- Tkinter (GUI)
- CSV (Data Persistence)
- `datetime`, `timedelta` for rental duration handling
- `abc` module for abstract base classes

---

## 🚀 Getting Started

### Prerequisites
- Python 3 installed

### How to Run
1. Download or clone the repository.
2. Ensure the required `.csv` files (`users.csv`, `cars.csv`, `rentals.csv`, `feedback.csv`) are present or will be auto-generated.
3. Run the script:
```bash
python Car_Rental_Management_System_Updated.py
```

---

## 🔐 Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

---

## 📂 File Structure

```
📁 project/
├── Car_Rental_Management_System_Updated.py
├── users.csv
├── cars.csv
├── rentals.csv
├── feedback.csv
```

---

## ⚙️ Future Enhancements

- Migrate to a relational database (e.g., SQLite or MySQL)
- Develop a web-based version with Flask or Django
- Integrate email/SMS notifications
- Add vehicle maintenance 

---

## Acknowledgement

Special thanks to our course and lab instructors for their valuable feedback and support during the development of this project.

---

## 📄 License

This project is intended for educational purposes and is not licensed for commercial use.
