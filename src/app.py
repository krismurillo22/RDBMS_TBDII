from ui.main_window import MainWindow
from ui.theme import apply_theme

def main():
    app = MainWindow()
    apply_theme(app)
    app.mainloop()

if __name__ == "__main__":
    main()
