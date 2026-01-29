import tkinter as tk
from db.init_db import init_db
from db.connection import get_connection

# Inicializamos la BD
init_db()

# Tkinter básico
root = tk.Tk()
root.title("Mi App con CockroachDB")

label = tk.Label(root, text="Hola CockroachDB desde Tkinter!")
label.pack(padx=20, pady=20)

root.mainloop()
