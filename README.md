#🔍 Lost & Found Management System
##Akademia Finansów i Biznesu Vistula — Kawęczyńska 36, Warsaw
A desktop application for managing lost and found items at Vistula University. 
Built with Python using OOP principles, a SQLite database, and a Tkinter graphical interface.

#📋 Features (10 Functionalities)
#Functionality            #Details
01  User Registration      SHA-256 hashed passwords
02 Login & Logout           Session management
03 Register Lost Item       With optional image upload
04 Register Found Item      With optional image upload
05 Search & Filter          By name, category, location, type
06 Automatic Matching        Matches lost ↔ found by category + location
07 Claim an Item             Updates item status in database
08 Admin Dashboard           Live lost/found item counts
09 Claimed Items View        Full claims history table10Excel ExportExports items + claims to .xlsx

##🛠️ Tech Stack

Python 3 — core language
Tkinter — GUI framework
SQLite3 — local database
openpyxl — Excel report generation
Pillow — image handling in splash screen
hashlib — SHA-256 password hashing

##⚙️ OOP Concepts Used

Encapsulation — private attributes (_password_hash, _name) with @property getters
Abstraction — Item(ABC) abstract base class with @abstractmethod match()
Inheritance — LostItem and FoundItem both inherit from Item
Polymorphism — match() behaves differently in each subclass
Singleton Pattern — DatabaseManager maintains one DB connection throughout the app

