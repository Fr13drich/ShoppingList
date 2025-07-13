"""run gui"""
from gui import App


def on_closing():
    app.withdraw()
    app.quit()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()


