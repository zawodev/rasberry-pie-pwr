from admin_app import App

if __name__ == "__main__":
    import os
    path = os.path.join(os.getcwd(), "database.db")
    app = App(path)
    app.mainloop()
