import os
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from models import User, LostItem, FoundItem, Claim
from database import DatabaseManager
from utils import match_items, export_reports


class LostAndFoundApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lost and Found Dashboard")
        self.db = DatabaseManager()
        self.current_user = None
        self.show_splash_screen()

        # ==================== Splash Screen ====================

    def show_splash_screen(self):
        self.splash = tk.Toplevel(self.root)
        self.splash.title("Welcome")
        self.splash.configure(bg="#0a3d4f")

        # Center the splash window
        self.splash.geometry("600x350")
        self.splash.resizable(False, False)

        # Load and show the logo
        try:
            from PIL import Image, ImageTk
            img = Image.open("/Users/a1/Desktop/Vistula-Logo.png")
            img = img.resize((300, 120), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            tk.Label(self.splash, image=self.logo_img, bg="#0a3d4f").pack(pady=(40, 10))
        except Exception as e:
            print("IMAGE ERROR:", e)

        tk.Label(
            self.splash,
            text="Lost & Found System",
            font=("Arial", 38, "italic"),
            fg="#5bc8d1",  # light teal
            bg="#0a3d4f"
        ).pack(pady=(5, 5))

        tk.Label(
            self.splash,
            text="Kawęczyńska 36, Warsaw",
            font=("Georgia", 11),
            fg="#ffffff",
            bg="#0a3d4f"
        ).pack()

        self.splash.after(3000, self.destroy_splash)

    def destroy_splash(self):  # <-- make sure this is still here
        self.splash.destroy()
        self.create_login_screen()

    # ---------------- LOGIN / REGISTER ----------------
    def create_login_screen(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        tk.Label(self.login_window, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.pack()
        tk.Label(self.login_window, text="Password:").pack()
        self.password_entry = tk.Entry(self.login_window, show="*")
        self.password_entry.pack()
        tk.Button(self.login_window, text="Login", command=self.login).pack()
        tk.Button(self.login_window, text="Register", command=self.register).pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user_data = self.db.get_user(username)  # (id, username, password_hash)
        if user_data and User(username, password).check_password(password):
            self.current_user = User(username, password)
            self.current_user.db_id = user_data[0]
            self.login_window.destroy()
            self.create_admin_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.db.get_user(username):
            messagebox.showerror("Error", "Username already exists!")
            return
        user = User(username, password)
        self.db.add_user(user)
        messagebox.showinfo("Success", "Registered!")

    # ---------------- ADMIN DASHBOARD ----------------
    def create_admin_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        items = self.db.get_items()
        lost_count = len([i for i in items if i[1] == "lost"])
        found_count = len([i for i in items if i[1] == "found"])

        tk.Label(self.root, text="ADMIN DASHBOARD", font=("Times New Roman", 28)).pack(pady=10)
        tk.Label(self.root, text=f"Total Lost Items: {lost_count}", font=("Arial", 14)).pack(pady=5)
        tk.Label(self.root, text=f"Total Found Items: {found_count}", font=("Arial", 14)).pack(pady=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x")

        tk.Button(btn_frame, text="All Entries", width=20, command=self.create_main_dashboard).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Export Excel", width=20, command=export_reports).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Claimed Items", width=20, command=self.show_claimed_items).grid(row=1, column=0,
                                                                                         padx=10)
        tk.Button(btn_frame, text="Export All Items", width=20, command=export_reports).grid(row=1, column=1,
                                                                                                    padx=10)

        tk.Button(top_frame, text="Logout", command=self.logout).pack(side="right", padx=10)

    def logout(self):
        self.current_user = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_login_screen()

    # ---------------- MAIN DASHBOARD ----------------
    def create_main_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Search / Filter
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Name:").grid(row=0, column=0)
        self.search_name = tk.Entry(search_frame)
        self.search_name.grid(row=0, column=1)
        tk.Label(search_frame, text="Category:").grid(row=0, column=2)
        self.search_cat = tk.Entry(search_frame)
        self.search_cat.grid(row=0, column=3)
        tk.Label(search_frame, text="Location:").grid(row=0, column=4)
        self.search_loc = tk.Entry(search_frame)
        self.search_loc.grid(row=0, column=5)
        tk.Label(search_frame, text="Type:").grid(row=0, column=6)
        self.search_type = ttk.Combobox(search_frame, values=["lost", "found"])
        self.search_type.grid(row=0, column=7)
        tk.Button(search_frame, text="Search", command=self.perform_search).grid(row=0, column=8, padx=5)
        tk.Button(search_frame, text="Reset", command=self.reset_dashboard).grid(row=0, column=9, padx=5)

        # Treeview
        self.tree = ttk.Treeview(
            self.root,
            columns=("ID", "Type", "Name", "Category", "Date", "Location", "Status", "Image"),
            show="headings"
        )
        self.tree.bind("<Double-1>", self.view_image)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        self.load_items()

        # Actions
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        tk.Button(action_frame, text="Register Lost Item", command=self.show_lost_form).grid(row=0, column=0, padx=5)
        tk.Button(action_frame, text="Register Found Item", command=self.show_found_form).grid(row=0, column=1, padx=5)
        tk.Button(action_frame, text="View Matches", command=self.view_matches).grid(row=0, column=2, padx=5)
        tk.Button(action_frame, text="Claim Item", command=self.claim_item).grid(row=0, column=3, padx=5)
        tk.Button(action_frame, text="Export Reports", command=export_reports).grid(row=0, column=4, padx=5)
        tk.Button(action_frame, text="Back to Admin Dashboard", command=self.create_admin_dashboard).grid(row=0,
                                                                                                          column=5,
                                                                                                          padx=5)



        # Forms
        self.lost_form = tk.Frame(self.root)
        self.found_form = tk.Frame(self.root)
        self.setup_lost_form()
        self.setup_found_form()

    # ---------------- ITEM HANDLERS ----------------
    def load_items(self, filters=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        items = self.db.get_items(filters)

        for row in items:
            image_path = row[8]  # image_path column in DB
            view_text = "VIEW" if image_path else ""

            self.tree.insert("", tk.END, values=(
                row[0], row[1], row[2], row[4], row[5], row[6], row[7], view_text
            ))

    def perform_search(self):
        filters = {}
        if self.search_name.get(): filters["name"] = self.search_name.get()
        if self.search_cat.get(): filters["category"] = self.search_cat.get()
        if self.search_loc.get(): filters["location"] = self.search_loc.get()
        if self.search_type.get(): filters["type"] = self.search_type.get()
        self.load_items(filters)

    def reset_dashboard(self):
        self.search_name.delete(0, tk.END)
        self.search_cat.delete(0, tk.END)
        self.search_loc.delete(0, tk.END)
        self.search_type.set("")
        self.load_items()

    # ---------------- LOST/FOUND FORMS ----------------
    def show_lost_form(self):
        self.found_form.pack_forget()
        self.lost_form.pack(pady=10)

    def show_found_form(self):
        self.lost_form.pack_forget()
        self.found_form.pack(pady=10)

    def setup_lost_form(self):
        tk.Label(self.lost_form, text="Register Lost Item").grid(row=0, column=0, columnspan=2)
        tk.Label(self.lost_form, text="Name:").grid(row=1, column=0)
        self.lost_name = tk.Entry(self.lost_form); self.lost_name.grid(row=1, column=1)
        tk.Label(self.lost_form, text="Description:").grid(row=2, column=0)
        self.lost_desc = tk.Entry(self.lost_form); self.lost_desc.grid(row=2, column=1)
        tk.Label(self.lost_form, text="Category:").grid(row=3, column=0)
        self.lost_cat = tk.Entry(self.lost_form); self.lost_cat.grid(row=3, column=1)
        tk.Label(self.lost_form, text="Date (YYYY-MM-DD):").grid(row=4, column=0)
        self.lost_date = tk.Entry(self.lost_form); self.lost_date.grid(row=4, column=1)
        tk.Label(self.lost_form, text="Location:").grid(row=5, column=0)
        self.lost_loc = tk.Entry(self.lost_form); self.lost_loc.grid(row=5, column=1)
        tk.Button(self.lost_form, text="Submit", command=self.submit_lost_item).grid(row=6, column=0, columnspan=2)
        tk.Button(self.lost_form, text="Select Image", command=self.select_lost_image).grid(row=7, column=0, columnspan=2)
        self.lost_image_path = None

    def select_lost_image(self):
        self.lost_image_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if self.lost_image_path:
            messagebox.showinfo("Image", "Image selected")  # <- add this to confirm selection

    def select_found_image(self):
        self.found_image_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if self.found_image_path:
            messagebox.showinfo("Image", "Image selected")  # <- add this to confirm selection

    def setup_found_form(self):
        tk.Label(self.found_form, text="Register Found Item").grid(row=0, column=0, columnspan=2)
        tk.Label(self.found_form, text="Name:").grid(row=1, column=0)
        self.found_name = tk.Entry(self.found_form); self.found_name.grid(row=1, column=1)
        tk.Label(self.found_form, text="Description:").grid(row=2, column=0)
        self.found_desc = tk.Entry(self.found_form); self.found_desc.grid(row=2, column=1)
        tk.Label(self.found_form, text="Category:").grid(row=3, column=0)
        self.found_cat = tk.Entry(self.found_form); self.found_cat.grid(row=3, column=1)
        tk.Label(self.found_form, text="Date (YYYY-MM-DD):").grid(row=4, column=0)
        self.found_date = tk.Entry(self.found_form); self.found_date.grid(row=4, column=1)
        tk.Label(self.found_form, text="Location:").grid(row=5, column=0)
        self.found_loc = tk.Entry(self.found_form); self.found_loc.grid(row=5, column=1)
        tk.Button(self.found_form, text="Submit", command=self.submit_found_item).grid(row=6, column=0, columnspan=2)
        tk.Button(self.found_form, text="Select Image", command=self.select_found_image).grid(row=7, column=0, columnspan=2)
        self.found_image_path = None

# ------------------SELECT IMAGE AND  OPEN--------------

    def view_image(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0])["values"]
        item_id = values[0]

        item = self.db.get_item_by_id(item_id)
        image_path = item[8]

        if not image_path:
            messagebox.showinfo("No Image", "This item has no image.")
            return

        if not os.path.exists(image_path):
            messagebox.showerror("Error", "Image file not found.")
            return

        subprocess.run(["open", image_path])


    # ---------------- SUBMIT ITEMS ----------------
    def submit_lost_item(self):
        name = self.lost_name.get();
        desc = self.lost_desc.get()
        cat = self.lost_cat.get();
        date = self.lost_date.get();
        loc = self.lost_loc.get()
        if not all([name, desc, cat, date, loc]):
            messagebox.showerror("Error", "All fields are required!");
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")

            # --- Image handling ---
            image_to_save = None
            if self.lost_image_path:  # if an image was selected
                images_dir = "/Users/a1/PycharmProjects/LostnFound/images"
                os.makedirs(images_dir, exist_ok=True)
                filename = os.path.basename(self.lost_image_path)
                dest_path = os.path.join(images_dir, filename)
                shutil.copy(self.lost_image_path, dest_path)
                image_to_save = dest_path


            # Create LostItem with saved image path or None
            item = LostItem(name, desc, cat, date, loc, self.current_user.db_id, self.lost_image_path)
            self.db.add_item(item)


            messagebox.showinfo("Success", "Lost item registered!")
            self.load_items();
            self.clear_lost_form();
            self.lost_image_path = None
        except ValueError:
            messagebox.showerror("Error", "Invalid date format!")

    def submit_found_item(self):
        name = self.found_name.get();
        desc = self.found_desc.get()
        cat = self.found_cat.get();
        date = self.found_date.get();
        loc = self.found_loc.get()
        if not all([name, desc, cat, date, loc]):
            messagebox.showerror("Error", "All fields are required!");
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
            item = FoundItem(name, desc, cat, date, loc, self.current_user.db_id, self.found_image_path)
            self.db.add_item(item)
            messagebox.showinfo("Success", "Found item registered!")
            self.load_items();
            self.clear_found_form();
            self.found_image_path = None
        except ValueError:
            messagebox.showerror("Error", "Invalid date format!")

    # ---------------- CLEAR FORMS ----------------
    def clear_lost_form(self):
        self.lost_name.delete(0, tk.END); self.lost_desc.delete(0, tk.END)
        self.lost_cat.delete(0, tk.END); self.lost_date.delete(0, tk.END); self.lost_loc.delete(0, tk.END)

    def clear_found_form(self):
        self.found_name.delete(0, tk.END); self.found_desc.delete(0, tk.END)
        self.found_cat.delete(0, tk.END); self.found_date.delete(0, tk.END); self.found_loc.delete(0, tk.END)

    # ---------------- OTHER ACTIONS ----------------
    def view_matches(self):
        matches = match_items()
        if not matches:
            messagebox.showinfo("Matches", "No matches found."); return
        result = ""
        for lost, found in matches:
            result += f"Lost: {lost._name} ({lost._location})  ↔  Found: {found._name} ({found._location})\n"
        messagebox.showinfo("Matches", result)

    def claim_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an item")
            return

        item_id = self.tree.item(selected[0])["values"][0]

        claim = Claim(item_id, self.current_user.db_id)
        self.db.add_claim(claim)
        self.db.update_item_status(item_id, "claimed")

        messagebox.showinfo("Success", "Item claimed")
        self.load_items()

    def show_claimed_items(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="CLAIMED ITEMS", font=("Arial", 18)).pack(pady=10)

        tree = ttk.Treeview(self.root, columns=("ID", "Item ID", "Claimant ID", "Status", "Claim Date"),
                            show="headings")
        for col in tree["columns"]:
            tree.heading(col, text=col)
        tree.pack(fill=tk.BOTH, expand=True, pady=10)

        claimed_items = self.db.get_claims()
        for row in claimed_items:
            tree.insert("", tk.END, values=row)

        tk.Button(self.root, text="Back to Dashboard", command=self.create_admin_dashboard).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = LostAndFoundApp(root)
    root.mainloop()
