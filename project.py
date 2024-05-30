from tkinter import  Listbox, messagebox, END, PhotoImage, Label, W, filedialog
import customtkinter
import json
from datetime import date, datetime
from tkinter import Entry,StringVar,IntVar,Checkbutton,Button,Tk
import sqlite3
# Database functions
def create_table():
    conn = sqlite3.connect('cake.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Customers (
                        id INTEGER PRIMARY KEY,
                        cash INTEGER,
                        datetime TEXT,
                        items TEXT
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT
            )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS login_logs(
                   id INTEGER PRIMARY KEY,
                   username TEXT,
                   login_time TEXT,
                   logout_time TEXT)''')
    conn.commit()
    conn.close()


def insert_login_log(username, login_time):
    conn = sqlite3.connect('cake.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO login_logs(username, login_time) VALUES (?, ?)', (username, login_time))
    conn.commit()
    conn.close()

def insert_logout_log(username, logout_time):
    conn = sqlite3.connect('cake.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE login_logs SET logout_time = ? WHERE username = ? AND logout_time IS NULL", (logout_time, username))
    conn.commit()
    conn.close()

def insert_customer(cash, datetime, items):
    conn = sqlite3.connect('cake.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Customers (cash, datetime, items) VALUES (?, ?, ?)",
                   (cash, datetime, items))
    conn.commit()
    conn.close()

# Database functions for menu items
def insert_menu_item(name, price, description):
    conn = sqlite3.connect('cake.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO menu_items(name, price, description) VALUES (?, ?, ?)', (name, price, description))
    conn.commit()
    conn.close()

def update_menu_item_in_db(id, name, price, description):
    conn = sqlite3.connect('cake.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE menu_items SET name = ?, price = ?, description = ? WHERE id = ?', (name, price, description, id))
    conn.commit()
    conn.close()

def delete_menu_item_from_db(id):
    conn = sqlite3.connect('cake.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM menu_items WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def fetch_menu_items():
    conn = sqlite3.connect('cake.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu_items')
    menu_items = cursor.fetchall()
    conn.close()
    return menu_items


create_table()
app = customtkinter.CTk()
app.title("CAKE BAKESHOP")
app.geometry("880x600+200+20")
app.resizable(0, 0)

# Define global variables
login_window = None
authenticated = False
# To set background image, you need to use a Label widget and place the image on it
bg_image = PhotoImage(file="bg.png")
bg_label = Label(app, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

bill_frame = customtkinter.CTkFrame(app, width=350, height=690, fg_color='black')
bill_frame.place(x=550, y=0)

# Change the background of the bill_frame to an image
bill_bg_image = PhotoImage(file="chocolate_cake.png")
bill_bg_label = Label(bill_frame, image=bill_bg_image)
bill_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Fonts
font2 = ('ARIAL', 10, 'bold')
font3 = ('ARIAL', 12, 'bold')
font4 = ('time new roman', 20, 'bold')
font5 = ('time new roman', 19, 'bold')
font6=('time new roman', 12, 'bold')

menu_label = customtkinter.CTkLabel(app, text="WELCOME TO ANGEL TIU\nCAKE BAKESHOP", font=font4, text_color="blue", fg_color="pink")
menu_label.place(x=100, y=0)
menu_file = "menu.json"

# Load menu items from file or create an empty list
try:
    with open(menu_file, "r") as file:
        menu_items = json.load(file)
except FileNotFoundError:
    menu_items = []

# Dictionary to store selected items and quantities
selected_items = {}


def update_menu_listbox():
    menu_listbox.delete(0, END)
    for item in menu_items:
        # Format the price with two decimal places
        formatted_price = "{:.2f}".format(item['price'])
        menu_listbox.insert(END, f"{item['name']} - ₱{formatted_price}")
        
menu_listbox = Listbox(app, font=font5, bg="pink", fg="black", width=25, height=10)
menu_listbox.place(x=5, y=100)
update_menu_listbox()



# Function to save menu items to file
def save_menu():
    with open(menu_file, "w") as file:
        json.dump(menu_items, file)


def add_menu_item():
    name = name_entry.get()
    price = price_entry.get()
    description = description_entry.get()
    if name.strip() == "" or price.strip() == "" or description.strip() == "":
        messagebox.showerror("Error", "Please enter item name, price, and description.")
        return
    try:
        price = float(price)
    except ValueError:
        messagebox.showerror("Error", "Invalid price. Please enter a valid number.")
        return
    menu_items.append({"name": name, "price": price, "description": description})  # Update the local list
    update_menu_listbox()
    save_menu()  # Save data to the file
    insert_menu_item(name, price, description)  # Save data to the database
    clear_entry_fields()



def delete_menu_item():
    selected_index = menu_listbox.curselection()
    if selected_index:
        # Get the ID of the item to be deleted
        item_id = selected_index[0] + 1  # Assuming IDs start from 1
        # Delete the item from the database
        delete_menu_item_from_db(item_id)
        # Delete the item from the menu_items list
        del menu_items[selected_index[0]]
        # Update the menu listbox
        update_menu_listbox()
        update_total_amount()
        # Save the updated menu to the file
        save_menu()



def delete_selected_item():
    selected_index = cart_listbox.curselection()
    if selected_index:
        # Get the item name and quantity from the selected item
        selected_item = cart_listbox.get(selected_index[0])
        item_name, _ = selected_item.split(" - ")

        # Remove the item from the selected_items dictionary
        if item_name in selected_items:
            del selected_items[item_name]

        # Delete the item from the cart_listbox
        cart_listbox.delete(selected_index)

        # Clear the entry fields
        clear_entry_fields()




def update_total_amount():
    total_amount = 0
    for item_name, quantity in selected_items.items():
        for menu_item in menu_items:
            if menu_item['name'] == item_name:
                item_price = menu_item['price']
                item_amount = quantity * item_price
                total_amount += item_amount

    # Clear the existing total amount entry
    cart_listbox.delete(cart_listbox.size() - 1)

    # Insert the updated total amount
    cart_listbox.insert(END, f"Total Amount: ₱{total_amount:.2f}")

def update_menu_item():
    selected_index = menu_listbox.curselection()
    if selected_index:
        name = name_entry.get()
        price = price_entry.get()
        description = description_entry.get()
        if name.strip() == "" or price.strip() == "" or description.strip() == "":
            messagebox.showerror("Error", "Please enter item name, price, and description.")
            return
        try:
            price = float(price)
        except ValueError:
            messagebox.showerror("Error", "Invalid price. Please enter a valid number.")
            return
        menu_items[selected_index[0]]["price"] = price
        menu_items[selected_index[0]]["description"] = description
        update_menu_listbox()
        save_menu()
        
        # Update the item in the database
        item_id = selected_index[0] + 1  # Assuming IDs start from 1
        update_menu_item_in_db(item_id, name, price, description)
        
        clear_entry_fields()

# Function to clear entry fields
def clear_entry_fields():
    name_entry.delete(0, END)
    price_entry.delete(0, END)
  
def clear_all_fields():
    name_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)
    cash_entry.delete(0, END)
    description_entry.delete(0, END)

    # Clear the selected items dictionary
    selected_items.clear()

    # Clear the cart items
    cart_items.clear()
    

    # Update the cart listbox
    update_cart_listbox()
    

    # Clear the receipt label if it exists
    for widget in bill_frame.winfo_children():
        if isinstance(widget, customtkinter.CTkLabel):
            widget.destroy()
# Define a global variable to hold the cart items
cart_items = []
def update_cart_listbox():
    cart_listbox.delete(0, END)
    total_amount = 0  # Variable to store the total amount of all items in the cart
    for item_name, quantity in selected_items.items():
        for menu_item in menu_items:
            if menu_item['name'] == item_name:
                item_price = menu_item['price']
                item_amount = quantity * item_price
                total_amount += item_amount
                cart_listbox.insert(END, f"{quantity} {item_name} - ₱{item_amount:.2f}")  # Display item quantity and amount
    cart_listbox.insert(END, f"Total Amount: ₱{total_amount:.2f}")  # Display total amount

# Create a new Listbox for displaying cart items
cart_listbox = Listbox(app, font=font5, bg="pink", fg="black", width=25, height=10)
cart_listbox.place(x=370, y=100)
update_cart_listbox()

def add_to_cart():
    selected_index = menu_listbox.curselection()
    if not selected_index:
        messagebox.showerror("Error", "Please select an item from the menu.")
        return

    name = menu_items[selected_index[0]]["name"]
    quantity_str = quantity_entry.get()

    # Check if quantity entry is empty
    if not quantity_str:
        messagebox.showerror("Error", "Please enter a quantity.")
        return

    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Invalid quantity. Please enter a positive integer.")
        return

    # Check if the item already exists in the cart
    if name in selected_items:
        # If it exists, increment the quantity
        selected_items[name] += quantity
    else:
        # If it doesn't exist, add it to the cart with the specified quantity
        selected_items[name] = quantity

    # Update cart listbox
    update_cart_listbox()
    
    # Update total amount
    update_total_amount()

    messagebox.showinfo("Success", f"{quantity} {name}(s) added to cart.")
    
def update_total_amount():
    total_amount = 0
    for item, quantity in selected_items.items():
        total_amount += menu_items[item]["price"] * quantity
    # Update total amount display here


def delete_item():
    delete_menu_item()
    if not selected_items:
        messagebox.showerror("Error", "Your cart is empty. Please select an item.")
        return
    
    
    
    delete_selected_item()
    # Clear the cart_listbox
    cart_listbox.delete(cart_items)

    # Recalculate the total amount
    update_total_amount()

def generate_receipt():
    if selected_items:
        # Calculate total price of items in the cart
        total_price = sum(menu_item["price"] * quantity for name, quantity in selected_items.items() for menu_item in menu_items if menu_item["name"] == name)
        
        # Check if cash entry is empty
        if not cash_entry.get():
            messagebox.showerror("Error", "Please enter a cash amount.")
            return None
        
        # Convert cash amount to float
        cash_amount = float(cash_entry.get())
        
        # Check if cash amount is sufficient
        if cash_amount >= total_price:
            # Generate receipt text
            receipt_text = f"""CARMERNS CAKESHOP
Address: Rizal Street Barangay Washington
cell_no: 09124492121
Date: {date.today()} {datetime.now().strftime('%H:%M:%S')}
{'*' * 70}
{'Qty':<12}{'Item':<30}{'Amount':>12}
{'*' * 70}\n"""
            item_names = []
            for name, quantity in selected_items.items():
                price = next(menu_item["price"] for menu_item in menu_items if menu_item["name"] == name)
                item_total = price * quantity
                receipt_text += f"{quantity:<12}{name:<30}₱{item_total:>12.2f}\n"
                item_names.append(name)
            receipt_text += f"\n{'*' * 70}\n"
            receipt_text += f"TOTAL{'':<42}₱{total_price:>15.2f}\n"
            receipt_text += f"CASH{'':<42}₱{cash_amount:>14.2f}\n"
            receipt_text += f"CHANGE{'':<40}₱{cash_amount - total_price:>12.2f}\n"
            receipt_text += f"{'*' * 70}\nTHANK YOUU!!\nHAVE A NICE DAY"
            
            # Call insert_customer to save transaction to the database
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            items_str = ", ".join(item_names)
            insert_customer(cash_amount, current_datetime, items_str)
            
            # Display receipt
            receipt_label = customtkinter.CTkLabel(bill_frame, text=receipt_text, font=font6, bg_color="white", width=320,
                                               anchor=W)
            receipt_label.place(x=0, y=180)

            return receipt_text
        else:
            messagebox.showerror("Insufficient Cash", "The cash amount entered is insufficient.")
            return None
    else:
        messagebox.showwarning("Error", "Your cart is empty.")
        return None


# Function to save the receipt
def save_receipt():
    receipt_text = generate_receipt()
    if receipt_text:
        # Ask the user to select the file path
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

        # Check if the user canceled the operation
        if file_path:
            # Write receipt text to the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(receipt_text)

            messagebox.showinfo("Success", f"Receipt saved as {file_path}")
    else:
        messagebox.showwarning("Error", "Your cart is empty. Cannot save receipt.")



# Listbox to display menu items
menu_listbox = Listbox(app, font=font5, bg="pink", fg="black", width=25, height=10)
menu_listbox.place(x=5, y=100)
update_menu_listbox()


# Frame for menu item management
frame = customtkinter.CTkFrame(app, bg_color='light yellow', fg_color='light yellow', corner_radius=10, border_width=2,
                                border_color='light yellow', width=700, height=200)
frame.place(x=25, y=345)

name_label = customtkinter.CTkLabel(frame, font=font2, text='Item Name:', text_color='white', bg_color='black')
name_label.place(x=50, y=10)

name_entry = customtkinter.CTkEntry(frame, font=font2, text_color='#000', fg_color='pink', border_color='#B2016C',
                                    border_width=2, width=160)
name_entry.place(x=10, y=40)

price_label = customtkinter.CTkLabel(frame, font=font2, text='Price:', text_color='white', bg_color='black')
price_label.place(x=210, y=10)

price_entry = customtkinter.CTkEntry(frame, font=font2, text_color='#000', fg_color='pink', border_color='#B2016C',
                                   border_width=2, width=80)
price_entry.place(x=190, y=40)

# Cash label and entry field
cash_label = customtkinter.CTkLabel(frame, text="Cash:", font=font2, text_color="white", bg_color="black")
cash_label.place(x=300, y=10)

cash_entry = customtkinter.CTkEntry(frame, font=font2, fg_color="pink", text_color="black", border_color='#B2016C',
                                    width=80)
cash_entry.place(x=280, y=40)

# Quantity label and entry field
quantity_label = customtkinter.CTkLabel(frame, text="Quantity:", font=font2, text_color="white", bg_color="black")
quantity_label.place(x=390, y=10)

quantity_entry = customtkinter.CTkEntry(frame, font=font2, fg_color="pink", text_color="black", border_color='#B2016C',
                                        width=80)
quantity_entry.place(x=380, y=40)
description_label = customtkinter.CTkLabel(frame, font=font2, text='Description:', text_color='white', bg_color='black')
description_label.place(x=500, y=10)

description_entry = customtkinter.CTkEntry(frame, font=font2, text_color='#000', fg_color='pink', border_color='#B2016C',
                                           border_width=2, width=160)
description_entry.place(x=460, y=40)

def show_description():
    selected_index = menu_listbox.curselection()
    if selected_index:
        index = selected_index[0]
        description = menu_items[index]["description"]
        messagebox.showinfo("Description", description)
    else:
        messagebox.showerror("Error", "Please select an item to view its description.")

show_description_button = customtkinter.CTkButton(frame, command=show_description, font=font2, text_color='black',
                                                  text='Show Description', fg_color='light blue', hover_color='white',
                                                  bg_color='pink', cursor='hand2', corner_radius=8, width=160)
show_description_button.place(x=500, y=100)


add_button = customtkinter.CTkButton(frame, command=add_menu_item, font=font2, text_color='black', text='Add',
                                     fg_color='light blue', hover_color='white', bg_color='pink', cursor='hand2',
                                     corner_radius=8, width=80)
add_button.place(x=15, y=100)

delete_button = customtkinter.CTkButton(frame, command=delete_item, font=font2, text_color='black',
                                        text='Delete', fg_color='light blue', hover_color='white', bg_color='pink',
                                        cursor='hand2', corner_radius=8, width=80)
delete_button.place(x=108, y=100)

update_button = customtkinter.CTkButton(frame, command=update_menu_item, font=font2, text_color='black',
                                        text='Update', fg_color='light blue', hover_color='white', bg_color='pink',
                                        cursor='hand2', corner_radius=8, width=80)
update_button.place(x=200, y=100)

clear_button = customtkinter.CTkButton(frame, command=clear_all_fields, font=font2, text_color='black',
                                       text='Clear', fg_color='light blue', hover_color='white', bg_color='pink',
                                       cursor='hand2', corner_radius=8, width=80)
clear_button.place(x=300, y=100)

# Button to add items to cart
add_to_cart_button = customtkinter.CTkButton(frame, command=add_to_cart, font=font2, text_color='black',
                                             text='Add to Cart', fg_color='light blue', hover_color='white',
                                             bg_color='pink', cursor='hand2', corner_radius=8, width=80)
add_to_cart_button.place(x=400, y=100)

# Payment button and entry fields
pay_button = customtkinter.CTkButton(frame, command=generate_receipt, font=font2, text_color='black', text='Pay',
                                     fg_color='light blue', hover_color='white', bg_color='pink', cursor='hand2',
                                     corner_radius=8, width=80)
pay_button.place(x=108, y=150)

# Button to save the receipt
save_receipt_button = customtkinter.CTkButton(frame, command=save_receipt, font=font2, text_color='black',
                                              text='Save Receipt', fg_color='light blue', hover_color='white',
                                              bg_color='pink', cursor='hand2', corner_radius=8, width=80)
save_receipt_button.place(x=200, y=150)
logout_button = customtkinter.CTkButton(frame, font=font2, text_color='black', text='logout', fg_color='light blue', hover_color='white', bg_color='pink', cursor='hand2', corner_radius=8, width=80)
logout_button.place(x=300, y=150)


app.mainloop()