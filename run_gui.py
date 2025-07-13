"""run gui"""
from gui import App

app = App()

def on_closing():
    """Clean exit"""
    app.withdraw()
    app.quit()

if __name__ == "__main__":
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()
