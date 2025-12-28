import csv
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

FIXED_ADMIN_USERNAME = "admin"
FIXED_ADMIN_PASSWORD = "admin123"
DEFAULT_ADMIN_BALANCE = 10000.0  # Default admin balance


class CSVStorable(ABC):
    """Abstract base class for all CSV-storable objects"""

    @abstractmethod
    def save_to_csv(self):
        pass


# File paths
USERS_FILE = "users.csv"
CARS_FILE = "cars.csv"
RENTALS_FILE = "rentals.csv"
FEEDBACK_FILE = "feedback.csv"


def read_csv(file_path):
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.DictReader(file) #reading data as dictionaries
            return list(reader)
    except FileNotFoundError:
        return []


def write_csv(file_path, data, fieldnames):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames) #writing data as dictionaries
        writer.writeheader()
        writer.writerows(data)


class Feedback(CSVStorable):
    def __init__(self, username, car_model, feedback_text, timestamp):
        self.username = username
        self.car_model = car_model
        self.feedback_text = feedback_text
        self.timestamp = timestamp

    def save_to_csv(self):
        feedbacks = read_csv(FEEDBACK_FILE) #reading csv file
        fieldnames = ["username", "car_model", "feedback_text", "timestamp"]
        feedbacks.append({
            "username": self.username,
            "car_model": self.car_model,
            "feedback_text": self.feedback_text,
            "timestamp": self.timestamp
        })
        write_csv(FEEDBACK_FILE, feedbacks, fieldnames)


class User(CSVStorable):
    def __init__(self, username, password, first_name, last_name, address, balance, role="customer"): #instance attributes for customer while registering
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.balance = float(balance)
        self.role = role

    def save_to_csv(self):
        users = read_csv(USERS_FILE) #read csv file
        fieldnames = ["username", "password", "first_name", "last_name", "address", "balance", "role"]

        # Update existing user or add new user
        user_found = False
        for user in users:
            if user["username"] == self.username:
                user.update(self.__dict__)
                user_found = True
                break

        if not user_found:
            users.append(self.__dict__)

        write_csv(USERS_FILE, users, fieldnames)

    @staticmethod # Helps to call method directly on the class itself without needing any instance of it
    def authenticate(username, password):
        # check fixed admin credentials
        if username == FIXED_ADMIN_USERNAME and password == FIXED_ADMIN_PASSWORD:
            users = read_csv(USERS_FILE)
            admin_user = next((user for user in users if user["username"] == FIXED_ADMIN_USERNAME), None)

            if admin_user:
                return User(
                    admin_user["username"],
                    admin_user["password"],
                    admin_user["first_name"],
                    admin_user["last_name"],
                    admin_user["address"],
                    admin_user["balance"],
                    admin_user.get("role", "admin").strip().lower()
                )
            else:
                # Create admin user if not exists
                admin_user = User(
                    FIXED_ADMIN_USERNAME,
                    FIXED_ADMIN_PASSWORD,
                    "Admin", "User",
                    "System", DEFAULT_ADMIN_BALANCE,
                    "admin"
                )
                admin_user.save_to_csv()
                return admin_user

        # Check regular users
        users = read_csv(USERS_FILE)
        for user in users:
            if user["username"] == username and user["password"] == password:
                return User(
                    user["username"],
                    user["password"],
                    user["first_name"],
                    user["last_name"],
                    user["address"],
                    user["balance"],
                    user.get("role", "customer").strip().lower()
                )
        return None


class Car(CSVStorable):
    def __init__(self, brand, model, seating_capacity, rental_price_per_day, is_available="True"):
        self.brand = brand
        self.model = model
        self.seating_capacity = int(seating_capacity)
        self.rental_price_per_day = float(rental_price_per_day)
        self.is_available = is_available

    def save_to_csv(self):
        cars = read_csv(CARS_FILE)
        fieldnames = ["brand", "model", "seating_capacity", "rental_price_per_day", "is_available"]
        cars.append(self.__dict__)
        write_csv(CARS_FILE, cars, fieldnames)

    @staticmethod # Helps to call method directly on the class itself without needing any instance of it
    def get_available_cars():
        return [car for car in read_csv(CARS_FILE) if car["is_available"] == "True"]


class Rental(CSVStorable): #Rental Class
    def __init__(self, username, car_model, start_date, end_date, rent_amount): #Instance attributes for rental class
        self.username = username
        self.car_model = car_model
        self.start_date = start_date
        self.end_date = end_date
        self.rent_amount = float(rent_amount)

    def save_to_csv(self):
        rentals = read_csv(RENTALS_FILE) #reads the csv file
        fieldnames = ["username", "car_model", "start_date", "end_date", "rent_amount"]
        rentals.append(self.__dict__)
        write_csv(RENTALS_FILE, rentals, fieldnames)


class AdminPanel: #AdminPanel Class
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Panel")

        tk.Label(root, text="Admin Panel", font=("Arial", 14)).pack()
        tk.Button(root, text="Add Car", command=self.add_car).pack()
        tk.Button(root, text="Remove Car", command=self.remove_car).pack()
        tk.Button(root, text="View All Customer Rentals", command=self.view_all_rentals).pack()
        tk.Button(root, text="View All Reserved Cars", command=self.view_reserved_cars).pack()
        tk.Button(root, text="View Feedback", command=self.view_feedback).pack()
        tk.Button(root, text="Set Rental Balance", command=self.set_admin_balance).pack(pady=5)
        tk.Button(root, text="View Current Balance", command=self.view_current_balance).pack(pady=5)

    def view_current_balance(self):
        users = read_csv(USERS_FILE) #read csv file
        admin_user = next((user for user in users if user["username"] == FIXED_ADMIN_USERNAME), None) #Next function helps to iterate over the list
        if admin_user:
            messagebox.showinfo("Current Balance", f"Your current balance is: ${float(admin_user['balance']):.2f}")
        else:
            messagebox.showinfo("Current Balance", f"Your current balance is: ${DEFAULT_ADMIN_BALANCE:.2f}")

    def set_admin_balance(self):
        """Set admin's rental balance with validation"""
        new_balance = simpledialog.askfloat( #simple dialog pop up asking for float input
            "Admin Balance",
            "Enter your rental balance amount:",
            minvalue=0  # Prevent negative values
        )

        if new_balance is not None:  # If user didn't cancel
            users = read_csv(USERS_FILE)
            admin_found = False

            for user in users:
                if user["username"] == FIXED_ADMIN_USERNAME:
                    user["balance"] = str(new_balance)
                    admin_found = True
                    break

            # If admin not found in users.csv, create a new entry
            if not admin_found:
                admin_user = {
                    "username": FIXED_ADMIN_USERNAME,
                    "password": FIXED_ADMIN_PASSWORD,
                    "first_name": "Admin",
                    "last_name": "User",
                    "address": "System",
                    "balance": str(new_balance),
                    "role": "admin"
                }
                users.append(admin_user)

            write_csv(USERS_FILE, users,
                      ["username", "password", "first_name", "last_name",
                       "address", "balance", "role"])

            messagebox.showinfo("Success", f"Balance set to ${new_balance:.2f}")

    def view_feedback(self):
        feedbacks = read_csv(FEEDBACK_FILE) #read csv file

        if not feedbacks:
            messagebox.showinfo("No Feedback", "No feedback submitted yet.")
            return

        feedback_win = tk.Toplevel(self.root) #creates new window which floats over main window
        feedback_win.title("Customer Feedback")
        feedback_win.geometry("700x500")

        main_frame = tk.Frame(feedback_win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        feedback_text = tk.Text(
            main_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        feedback_text.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=feedback_text.yview)

        for fb in feedbacks:
            feedback_text.insert(tk.END,
                                 f"Customer: {fb['username']}\n"
                                 f"Car Model: {fb['car_model']}\n"
                                 f"Date: {fb['timestamp']}\n"
                                 f"Feedback:\n{fb['feedback_text']}\n"
                                 f"{'=' * 50}\n\n"
                                 )

        feedback_text.config(state=tk.DISABLED)

        close_btn = tk.Button(
            feedback_win,
            text="Close",
            command=feedback_win.destroy,
            width=15
        )
        close_btn.pack(pady=10)

    def add_car(self):
        try:
            brand = simpledialog.askstring("Add Car", "Enter Car Brand:") #simple dialog pop up asking for string input
            model = simpledialog.askstring("Add Car", "Enter Car Model:")#simple dialog pop up asking for string input
            seating_capacity = simpledialog.askinteger("Add Car", "Enter Seating Capacity:")#simple dialog pop up asking for int input
            rental_price = simpledialog.askfloat("Add Car", "Enter Rental Price Per Day:")#simple dialog pop up asking for float input

            if not all([brand, model, seating_capacity, rental_price]):
                messagebox.showerror("Input Error", "All fields are required!")
                return

            if rental_price < 0:
                messagebox.showerror("Input Error", "Rental price must be positive!")
                return

            if seating_capacity <= 0:
                messagebox.showerror("Input Error", "Seating capacity must be at least 1!")
                return

            new_car = Car(brand, model, seating_capacity, rental_price)
            new_car.save_to_csv()
            messagebox.showinfo("Success", f"Car {brand} {model} added successfully!")

        except ValueError as ve:
            messagebox.showerror("Value Error", f"Invalid input: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")

    def remove_car(self):
        try:
            model_name = simpledialog.askstring("Remove Car", "Enter Model Name to Remove:") #simple dialog pop up asking for string input
            if not model_name:
                messagebox.showerror("Input Error", "Model name is required!")
                return

            cars = read_csv(CARS_FILE) #read csv file
            updated_cars = [car for car in cars if car["model"].lower() != model_name.lower()]

            if len(updated_cars) == len(cars):
                messagebox.showerror("Not Found", f"No car found with model: {model_name}")
                return

            write_csv(CARS_FILE, updated_cars,
                      ["brand", "model", "seating_capacity", "rental_price_per_day", "is_available"])
            messagebox.showinfo("Success", f"Car {model_name} removed successfully!")

        except FileNotFoundError:
            messagebox.showerror("File Error", "Car data file not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")

    def view_all_rentals(self):
        rentals = read_csv(RENTALS_FILE) #read csv file
        if not rentals:
            messagebox.showinfo("No Rentals", "No rentals found!")
            return

        rental_win = tk.Toplevel(self.root) #create new window which floats over main window
        rental_win.title("All Rentals")
        rental_win.geometry("800x600")

        main_frame = tk.Frame(rental_win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        rental_text = tk.Text(
            main_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        rental_text.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=rental_text.yview)

        for r in rentals:
            rental_text.insert(tk.END,
                               f"User: {r['username']}\n"
                               f"Car Model: {r['car_model']}\n"
                               f"From: {r['start_date']} | To: {r['end_date']}\n"
                               f"Amount: ${r['rent_amount']}\n"
                               f"{'=' * 50}\n\n"
                               )

        rental_text.config(state=tk.DISABLED) # disabled mode indicates the display in read-only mode

        close_btn = tk.Button(
            rental_win,
            text="Close",
            command=rental_win.destroy,
            width=15
        )
        close_btn.pack(pady=10)

    def view_reserved_cars(self):
        cars = read_csv(CARS_FILE) #read csv file
        reserved_cars = [car for car in cars if car["is_available"] == "False"]

        if not reserved_cars:
            messagebox.showinfo("No Reserved Cars", "No cars are currently reserved.")
            return

        reserved_win = tk.Toplevel(self.root) #create new window which floats over main window
        reserved_win.title("Reserved Cars")
        reserved_win.geometry("700x500")

        main_frame = tk.Frame(reserved_win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        reserved_text = tk.Text(
            main_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        reserved_text.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=reserved_text.yview)

        for car in reserved_cars:
            reserved_text.insert(tk.END,
                                 f"Brand: {car['brand']}\n"
                                 f"Model: {car['model']}\n"
                                 f"Seats: {car['seating_capacity']}\n"
                                 f"Price/day: ${car['rental_price_per_day']}\n"
                                 f"{'=' * 50}\n\n"
                                 )

        reserved_text.config(state=tk.DISABLED)

        close_btn = tk.Button(
            reserved_win,
            text="Close",
            command=reserved_win.destroy,
            width=15
        )
        close_btn.pack(pady=10)


class CarRentalApp:
    def __init__(self, root):
        self.root = root # instance  of Tkinter
        self.root.title("Online Car Rental System")

        self.label = tk.Label(root, text="Welcome to Car Rental System", font=("Arial", 14))
        self.label.pack()

        self.login_button = tk.Button(root, text="Login", command=self.show_login)
        self.login_button.pack()

        self.register_button = tk.Button(root, text="Register", command=self.show_register)
        self.register_button.pack()

    def view_feedback(self):
        feedbacks = read_csv(FEEDBACK_FILE) #read csv file
        if not feedbacks:
            messagebox.showinfo("Info", "No feedback yet")
            return

        all_feedback = "\n\n".join(
            f"User: {fb['username']}\nCar: {fb['car_model']}\n"
            f"Feedback: {fb['feedback_text']}\nDate: {fb['timestamp']}\n"
            for fb in feedbacks
        )
        messagebox.showinfo("Feedback", all_feedback)

    def return_car(self, user):
        rentals = read_csv(RENTALS_FILE) #read csv file
        user_rentals = [r for r in rentals if r["username"] == user.username and r["end_date"] == "Ongoing"]

        if not user_rentals:
            messagebox.showinfo("Return Car", "No ongoing rentals to return.")
            return

        car_model = simpledialog.askstring("Return Car", "Enter car model to return:") # dialog pops up asking for string input
        rental = next((r for r in user_rentals if r["car_model"].lower() == car_model.lower()), None) #loop run for each car in "cars" list

        if not rental:
            messagebox.showerror("Error", "Rental not found.")
            return

        expected_days = 1  # assume rental was for 1 day
        rented_date = datetime.strptime(rental["start_date"], "%Y-%m-%d")
        current_date = datetime.now()
        days_rented = (current_date - rented_date).days

        extra_fee = 0
        if days_rented > expected_days:
            extra_days = days_rented - expected_days
            extra_fee = extra_days * float(rental["rent_amount"])

        rental["end_date"] = current_date.strftime("%Y-%m-%d")
        write_csv(RENTALS_FILE, rentals, ["username", "car_model", "start_date", "end_date", "rent_amount"])

        cars = read_csv(CARS_FILE) #read csv file
        for car in cars:
            if car["model"] == rental["car_model"]:
                car["is_available"] = "True"
                break
        write_csv(CARS_FILE, cars, ["brand", "model", "seating_capacity", "rental_price_per_day", "is_available"])

        if extra_fee > 0:
            user.balance -= extra_fee
            messagebox.showinfo("Late Return", f"Returned late! Extra fee of ${extra_fee} deducted.")
        else:
            messagebox.showinfo("Return Success", "Car returned successfully!")

        users = read_csv(USERS_FILE) #read csv file
        for u in users:
            if u["username"] == user.username:
                u["balance"] = str(user.balance)
        write_csv(USERS_FILE, users, ["username", "password", "first_name", "last_name", "address", "balance", "role"])

    def show_register(self):
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Register")

        tk.Label(self.register_window, text="Username:").pack()
        self.reg_username = tk.Entry(self.register_window)
        self.reg_username.pack()

        tk.Label(self.register_window, text="Password:").pack()
        self.reg_password = tk.Entry(self.register_window, show="*")
        self.reg_password.pack()

        tk.Label(self.register_window, text="First Name:").pack()
        self.reg_first_name = tk.Entry(self.register_window)
        self.reg_first_name.pack()

        tk.Label(self.register_window, text="Last Name:").pack()
        self.reg_last_name = tk.Entry(self.register_window)
        self.reg_last_name.pack()

        tk.Label(self.register_window, text="Address:").pack()
        self.reg_address = tk.Entry(self.register_window)
        self.reg_address.pack()

        tk.Label(self.register_window, text="Balance:").pack()
        self.reg_balance = tk.Entry(self.register_window)
        self.reg_balance.pack()

        tk.Button(self.register_window, text="Register", command=self.register).pack()

    def register(self):
        try:
            username = self.reg_username.get()
            password = self.reg_password.get()
            first_name = self.reg_first_name.get()
            last_name = self.reg_last_name.get()
            address = self.reg_address.get()
            balance = self.reg_balance.get()

            if not all([username, password, first_name, last_name, address, balance]):
                messagebox.showerror("Error", "All fields are required!")
                return

            if username.lower() == FIXED_ADMIN_USERNAME.lower():
                messagebox.showerror("Error", "This username is reserved")
                return

            try:
                balance = float(balance)
                if balance < 0:
                    raise ValueError("Balance cannot be negative")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid balance: {e}")
                return

            users = read_csv(USERS_FILE) #read csv file
            if any(user["username"].lower() == username.lower() for user in users):
                messagebox.showerror("Error", "Username already exists!")
                return

            new_user = User(
                username,
                password,
                first_name,
                last_name,
                address,
                balance,
                "customer"
            )
            new_user.save_to_csv()

            messagebox.showinfo("Success", "Registration Successful!")
            self.register_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")

    def show_admin_panel(self):
        admin_window = tk.Toplevel(self.root)
        AdminPanel(admin_window)

    def show_login(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")

        tk.Label(self.login_window, text="Username:").pack()
        self.login_username = tk.Entry(self.login_window)
        self.login_username.pack()

        tk.Label(self.login_window, text="Password:").pack()
        self.login_password = tk.Entry(self.login_window, show="*")
        self.login_password.pack()

        tk.Button(self.login_window, text="Login", command=self.login).pack()

    def login(self):
        try:
            username = self.login_username.get()
            password = self.login_password.get()

            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password.")
                return

            user = User.authenticate(username, password)

            if user:
                messagebox.showinfo("Login Success", f"Welcome, {username}!")
                self.login_window.destroy()
                self.show_dashboard(user)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password")

        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Something went wrong:\n{str(e)}")

    def show_all_customers_rentals(self):
        rentals = read_csv(RENTALS_FILE)
        if not rentals:
            messagebox.showinfo("Customer Rentals", "No active rentals found.")
            return

        rental_info = "\n".join(
            [
                f"User: {r['username']} - Car: {r['car_model']} - From: {r['start_date']} - To: {r['end_date']} - Amount: ${r['rent_amount']}"
                for r in rentals]
        )
        messagebox.showinfo("Customer Rentals Report", rental_info)

    def show_reserved_cars(self):
        cars = read_csv(CARS_FILE)
        reserved_cars = [car for car in cars if car["is_available"] == "False"]

        if not reserved_cars:
            messagebox.showinfo("Reserved Cars", "No cars are currently reserved.")
            return

        car_list = "\n".join(
            [
                f"{car['brand']} {car['model']} - Seats: {car['seating_capacity']} - Price: ${car['rental_price_per_day']} per day"
                for car in reserved_cars]
        )
        messagebox.showinfo("Reserved Cars Report", car_list)

    def show_dashboard(self, user):
        self.dashboard_window = tk.Toplevel(self.root)
        self.dashboard_window.title("Dashboard")

        tk.Label(self.dashboard_window, text=f"Welcome, {user.first_name} {user.last_name}").pack()
        tk.Button(self.dashboard_window, text="View Available Cars", command=self.show_available_cars).pack()
        tk.Button(self.dashboard_window, text="Rent a Car", command=lambda: self.rent_car(user)).pack()
        tk.Button(self.dashboard_window, text="View Rental History",
                  command=lambda: self.view_rental_history(user)).pack()
        tk.Button(self.dashboard_window, text="Give Feedback", command=lambda: self.give_feedback(user)).pack()

        if user.role == "admin":
            tk.Button(self.dashboard_window, text="Add Car", command=self.add_car).pack()
            tk.Button(self.dashboard_window, text="Remove Car", command=self.remove_car).pack()
            tk.Button(self.dashboard_window, text="View All Customers Rentals",
                      command=self.show_all_customers_rentals).pack()
            tk.Button(self.dashboard_window, text="View All Reserved Cars", command=self.show_reserved_cars).pack()
            tk.Button(self.dashboard_window, text="Return Car", command=lambda: self.return_car(user)).pack()
            tk.Button(self.dashboard_window, text="View Feedback", command=self.view_feedback).pack()
            tk.Button(self.dashboard_window, text="Set Rental Balance", command=self.set_admin_balance).pack(pady=5)
            tk.Button(self.dashboard_window, text="View Current Balance",
                      command=lambda: self.view_current_balance(user)).pack(pady=5)

        tk.Button(self.dashboard_window, text="Logout", command=self.dashboard_window.destroy).pack()

    def view_current_balance(self, user):
        messagebox.showinfo("Current Balance", f"Your current balance is: ${user.balance:.2f}")

    def set_admin_balance(self):
        """Method to set admin's balance from the dashboard"""
        users = read_csv(USERS_FILE)
        admin_user = next((user for user in users if user["username"] == FIXED_ADMIN_USERNAME), None)

        if not admin_user:
            messagebox.showerror("Error", "Admin user not found!")
            return

        new_balance = simpledialog.askfloat(
            "Set Balance",
            "Enter new rental balance:",
            minvalue=0
        ) #A simple dialog box pop up asking for float input

        if new_balance is not None:
            for user in users:
                if user["username"] == FIXED_ADMIN_USERNAME:
                    user["balance"] = str(new_balance)
                    break

            write_csv(USERS_FILE, users,
                      ["username", "password", "first_name", "last_name",
                       "address", "balance", "role"])

            messagebox.showinfo("Success", f"Balance set to ${new_balance:.2f}")

    def add_car(self):
        try:
            brand = simpledialog.askstring("Add Car", "Enter car brand:")
            model = simpledialog.askstring("Add Car", "Enter car model:")
            seating_capacity = simpledialog.askinteger("Add Car", "Enter seating capacity:")
            rental_price_per_day = simpledialog.askfloat("Add Car", "Enter rental price per day:")

            if not (brand and model and seating_capacity and rental_price_per_day):
                messagebox.showerror("Error", "All fields are required!")
                return
            if seating_capacity is None or seating_capacity <= 0 or rental_price_per_day is None or rental_price_per_day <= 0:
                messagebox.showerror("Error", "Number you have entered must be positive")
                return

            car = Car(brand, model, seating_capacity, rental_price_per_day, "True")
            car.save_to_csv()

            messagebox.showinfo("Success", f"{brand} {model} added successfully!")

        except ValueError:
            messagebox.showerror("Input Error", "Invalid number for seating capacity or rental price.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Something went wrong:\n{str(e)}")

    def give_feedback(self, user):
        rentals = read_csv(RENTALS_FILE) #read csv file
        user_rentals = [r for r in rentals if r["username"] == user.username]

        if not user_rentals:
            messagebox.showinfo("No Rentals", "You must rent a car before giving feedback.")
            return

        car_model = simpledialog.askstring("Feedback", "Enter the car model you want to review:")
        rental_found = any(r["car_model"].lower() == car_model.lower() for r in user_rentals)

        if not rental_found:
            messagebox.showerror("Error", "You haven't rented this car model.")
            return

        feedback_text = simpledialog.askstring("Feedback", "Enter your feedback about the car and service:")
        if not feedback_text:
            messagebox.showerror("Error", "Feedback cannot be empty.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fb = Feedback(user.username, car_model, feedback_text, timestamp)
        fb.save_to_csv()

        messagebox.showinfo("Thank You!", "Thankyou for your feedback.")

    def remove_car(self):
        try:
            cars = read_csv(CARS_FILE) #read csv file
            car_model = simpledialog.askstring("Remove Car", "Enter car model to remove:") # a simple dialog box pop up asking for string input

            if not car_model:
                messagebox.showerror("Error", "Car model is required!")
                return

            updated_cars = [car for car in cars if car["model"].lower() != car_model.lower()]

            if len(updated_cars) == len(cars):
                messagebox.showerror("Error", "Car not found!")
                return

            write_csv(CARS_FILE, updated_cars,
                      ["brand", "model", "seating_capacity", "rental_price_per_day", "is_available"])

            messagebox.showinfo("Success", f"{car_model} removed successfully!")

        except FileNotFoundError:
            messagebox.showerror("File Error", f"The file {CARS_FILE} was not found.")
        except PermissionError:
            messagebox.showerror("Permission Error", f"Cannot write to {CARS_FILE}. Please check file permissions.")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"Something went wrong:\n{str(e)}")

    def show_available_cars(self):
        cars = Car.get_available_cars()
        car_list = "\n".join(
            [f"{car['brand']} {car['model']} - ${car['rental_price_per_day']} per day" for car in cars])
        messagebox.showinfo("Available Cars", car_list if car_list else "No cars available")

    def rent_car(self, user):
        cars = Car.get_available_cars()
        if not cars:
            messagebox.showerror("Error", "No cars available for rent.")
            return

        car_selection = simpledialog.askstring("Rent a Car", "Enter car model to rent:")
        selected_car = next((car for car in cars if car["model"].lower() == car_selection.lower()), None)

        if not selected_car:
            messagebox.showerror("Error", "Car not found.")
            return

        rental_price = float(selected_car["rental_price_per_day"])
        if user.balance < rental_price:
            messagebox.showerror("Error", "Insufficient balance.")
            return

        rental_days = simpledialog.askinteger("Rental Duration", "For how many days do you want to rent the car?")
        if not rental_days or rental_days <= 0:
            messagebox.showerror("Error", "Please enter a valid number of days.")
            return

        total_price = rental_price * rental_days

        if user.balance < total_price:
            messagebox.showerror("Error", f"Insufficient balance. Total cost would be ${total_price:.2f}")
            return

        payment_method = simpledialog.askstring(
            "Payment Method", "Choose Payment Method: Credit Card / Debit Card / Cash"
        ).lower() #a simple dialog box pop up asking for string input

        if payment_method not in ["credit card", "debit card", "cash"]: # payment method: debit or credit card
            messagebox.showerror("Payment Error", "Invalid payment method selected.")
            return

        if payment_method in ["credit card", "debit card"]: # payment method: debit or credit card
            card_number = simpledialog.askstring("Card Payment", "Enter your Card Number (16 digits):")
            expiry_date = simpledialog.askstring("Card Payment", "Enter Expiry Date (MM/YY):")
            cvv = simpledialog.askstring("Card Payment", "Enter CVV (3 digits):")

            if not card_number or len(card_number) != 16 or not card_number.isdigit():
                messagebox.showerror("Payment Error", "Invalid card number.")
                return
            if not expiry_date or len(expiry_date) != 5 or expiry_date[2] != '/':
                messagebox.showerror("Payment Error", "Invalid expiry date format.")
                return
            if not cvv or len(cvv) != 3 or not cvv.isdigit():
                messagebox.showerror("Payment Error", "Invalid CVV.")
                return

        elif payment_method == "cash": # payment method :cash
            messagebox.showinfo("Cash Payment", "Please pay the amount at the car pickup.")

        # Deduct the total price from user's balance
        user.balance -= total_price

        # Update car availability
        cars_data = read_csv(CARS_FILE)
        for car in cars_data:
            if car["model"] == selected_car["model"]:
                car["is_available"] = "False"
                break

        write_csv(CARS_FILE, cars_data, ["brand", "model", "seating_capacity", "rental_price_per_day", "is_available"])

        # Create rental record
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=rental_days)).strftime("%Y-%m-%d")
        rental = Rental(user.username, selected_car["model"], start_date, end_date, total_price)
        rental.save_to_csv()

        # Update user's balance in the database
        users = read_csv(USERS_FILE) #read csv file
        for u in users:
            if u["username"] == user.username:
                u["balance"] = str(user.balance)
                break
        write_csv(USERS_FILE, users, ["username", "password", "first_name", "last_name", "address", "balance", "role"])

        messagebox.showinfo("Success",
                            f"Payment Successful via {payment_method.title()}!\n"
                            f"You have rented {selected_car['model']} for {rental_days} days.\n"
                            f"Total cost: ${total_price:.2f}\n"
                            f"New balance: ${user.balance:.2f}")

    def view_rental_history(self, user):
        rentals = read_csv(RENTALS_FILE)
        user_rentals = [r for r in rentals if r["username"] == user.username]

        if not user_rentals:
            messagebox.showinfo("Rental History", "No rental history available.")
            return

        rental_info = "\n".join(
            [f"{r['car_model']} - {r['start_date']} to {r['end_date']} - ${r['rent_amount']}" for r in user_rentals])
        messagebox.showinfo("Rental History", rental_info)


if __name__ == "__main__": # helps to run whole program
    root = tk.Tk()
    app = CarRentalApp(root)
    root.mainloop()