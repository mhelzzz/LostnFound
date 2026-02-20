from openpyxl import Workbook
from models import LostItem, FoundItem
from database import DatabaseManager
from tkinter import filedialog, messagebox


def match_items():
    db = DatabaseManager()
    rows = db.get_items()

    lost_items = []
    found_items = []

    for row in rows:
        if row[1] == "lost":
            lost_items.append(LostItem(row[2], row[3], row[4], row[5], row[6],row[9], row[8]))
        elif row[1] == "found":
            found_items.append(FoundItem(row[2], row[3], row[4], row[5], row[6],row[9], row[8]))

    matches = []
    for lost in lost_items:
        for found in found_items:
            if lost.match(found):
                matches.append((lost, found))

    return matches


def export_reports():
    db = DatabaseManager()

    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")]
    )

    if not file_path:
        return

    wb = Workbook()
    ws_items = wb.active
    ws_items.title = "Items"

    ws_items.append(["ID", "Type", "Name", "Description", "Category", "Date", "Location", "Status", "Image Path"])

    for row in db.get_items():
        ws_items.append(row)

    ws_claims = wb.create_sheet("Claims")
    ws_claims.append(["ID", "Item ID", "Claimant ID", "Status", "Date"])

    claims = db.get_claims()
    for c in claims:
        ws_claims.append(c)

    wb.save(file_path)
    messagebox.showinfo("Export", "Export successful!")
