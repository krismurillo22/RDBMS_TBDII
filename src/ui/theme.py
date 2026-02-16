from tkinter import ttk

def apply_theme(root):
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except:
        pass

    BG_MAIN   = "#0f172a"
    BG_PANEL  = "#111c2f"
    BG_TABLE  = "#0b1220"
    ROW_ALT   = "#132038"
    TEXT      = "#e5e7eb"
    MUTED     = "#94a3b8"
    BORDER    = "#22324a"
    SELECT_BG = "#1d4ed8"
    BORDER    = "#22324a"


    root.configure(bg=BG_MAIN)

    # Base
    style.configure(".", background=BG_MAIN, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("TFrame", background=BG_MAIN)
    style.configure("TPanedwindow", background=BG_MAIN)
    style.configure("TLabel", background=BG_MAIN, foreground=TEXT)

    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), background=BG_MAIN, foreground=TEXT)
    style.configure("Sub.TLabel", background=BG_MAIN, foreground=MUTED)
    style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"), background=BG_MAIN, foreground=TEXT)
    style.configure("Muted.TLabel", background=BG_MAIN, foreground=MUTED)
    style.configure(
        "Treeview",
        background=BG_TABLE,
        fieldbackground=BG_TABLE,
        foreground=TEXT,
        bordercolor=BORDER,
        borderwidth=1,
        rowheight=28
    )

    style.map(
        "Treeview",
        background=[("selected", SELECT_BG)],
        foreground=[("selected", "white")]
    )

    style.configure(
        "Treeview.Heading",
        background=BG_PANEL,
        foreground=TEXT,
        bordercolor=BORDER,
        font=("Segoe UI", 10, "bold")
    )

    style.configure("TButton",
        background=BG_PANEL, foreground=TEXT, borderwidth=1)

    style.configure("TEntry", fieldbackground=BG_TABLE, foreground=TEXT, 
                    bordercolor=BORDER, lightcolor=BORDER,darkcolor=BORDER)

    style.configure("TCombobox", fieldbackground=BG_TABLE, foreground=TEXT)

    style.map("TCombobox", fieldbackground=[("readonly", BG_TABLE)], foreground=[("readonly", TEXT)])

    style.map("TButton", background=[("active", "#1e293b")])
