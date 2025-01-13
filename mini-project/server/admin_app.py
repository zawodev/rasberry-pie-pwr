from database import create_connection, create_tables, add_user, get_all_login_records, get_all_requests, delete_request, get_all_users, delete_user
import tkinter as tk
from tkinter import ttk, messagebox

class App(tk.Tk):
    def __init__(self, db_path="mini-project/server/database.db"):
        super().__init__()
        self.title("Example App")

        # Połączenie z bazą i utworzenie tabel
        self.conn = create_connection(db_path)
        if self.conn:
            create_tables(self.conn)

        # Etykieta tytułowa
        label = tk.Label(self, text="Menu główne", font=("Arial", 16, "bold"))
        label.pack(pady=20)

        # 1) Przycisk: Dodanie nowego użytkownika
        btn_new_user = tk.Button(self, text="Add new user", width=20, command=self.show_add_user_window)
        btn_new_user.pack(pady=5)

        # 2) Przycisk: Wyświetlenie login_record (Ewidencja)
        btn_login_record = tk.Button(self, text="Show login record", width=20, command=self.show_login_record_window)
        btn_login_record.pack(pady=5)

        # 3) Przycisk: Obróbka (Process) Requests
        btn_requests = tk.Button(self, text="Process requests", width=20, command=self.show_requests_window)
        btn_requests.pack(pady=5)

        # 4) Przycisk: Wyświetlenie i usuwanie użytkowników
        btn_show_users = tk.Button(self, text="Show users", width=20, command=self.show_users_window)
        btn_show_users.pack(pady=5)

    # -------------------------------------------------------
    # 1) Okno do dodawania nowego użytkownika (ręcznie)
    # -------------------------------------------------------
    def show_add_user_window(self):
        win = tk.Toplevel(self)
        win.title("Add new user")

        tk.Label(win, text="User ID (tekstowy):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(win, text="Login:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Label(win, text="Password:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Label(win, text="Safe Combination (RGB):\nWpisz 8 krotek np. (255,0,0),...").grid(row=3, column=0, sticky="w", padx=5, pady=5)

        entry_user_id = tk.Entry(win, width=30)
        entry_login = tk.Entry(win, width=30)
        entry_password = tk.Entry(win, show="*", width=30)
        entry_safe_comb = tk.Entry(win, width=60)

        entry_user_id.grid(row=0, column=1, padx=5, pady=5)
        entry_login.grid(row=1, column=1, padx=5, pady=5)
        entry_password.grid(row=2, column=1, padx=5, pady=5)
        entry_safe_comb.grid(row=3, column=1, padx=5, pady=5)

        def on_add():
            user_id = entry_user_id.get().strip()
            login = entry_login.get().strip()
            password = entry_password.get().strip()
            safe_str = entry_safe_comb.get().strip()

            if not user_id or not login or not password:
                messagebox.showerror("Error", "Uzupełnij wszystkie pola!")
                return

            try:
                # Parsujemy listę 8 krotek RGB z pola tekstowego
                safe_comb_list = eval(f"[{safe_str}]")  # uwaga - eval w demie
                if len(safe_comb_list) != 8:
                    raise ValueError("Musi być dokładnie 8 krotek RGB!")
            except Exception as e:
                messagebox.showerror("Error", f"Nieprawidłowy format Safe Combination:\n{e}")
                return

            # Dodanie do bazy
            add_user(self.conn, user_id, login, password, safe_comb_list)
            messagebox.showinfo("OK", f"Dodano nowego użytkownika: {user_id}")
            win.destroy()

        btn_save = tk.Button(win, text="Add User", command=on_add)
        btn_save.grid(row=4, column=1, pady=10, sticky="e")

    # -------------------------------------------------------
    # 2) Okno wyświetlające login_record (Ewidencja)
    # -------------------------------------------------------
    def show_login_record_window(self):
        win = tk.Toplevel(self)
        win.title("Login Record (Ewidencja)")

        records = get_all_login_records(self.conn)

        tree = ttk.Treeview(win, columns=("ewidencja_id", "user_id", "date_time", "status"), show="headings")
        tree.heading("ewidencja_id", text="Ewidencja ID")
        tree.heading("user_id", text="User ID")
        tree.heading("date_time", text="Date/Time")
        tree.heading("status", text="Status")

        tree.pack(fill="both", expand=True)

        for row in records:
            tree.insert("", tk.END, values=row)

    # -------------------------------------------------------
    # 3) Okno do obsługi Requests (Process requests)
    # -------------------------------------------------------
    def show_requests_window(self):
        win = tk.Toplevel(self)
        win.title("Process Requests")

        # Lewe okno: lista requestów
        frame_left = tk.Frame(win)
        frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame_left, text="List of requests:").pack(anchor="w")

        tree_req = ttk.Treeview(frame_left, columns=("request_id", "user_id", "date_time"), show="headings", height=10)
        tree_req.heading("request_id", text="Req ID")
        tree_req.heading("user_id", text="Requested user_id")
        tree_req.heading("date_time", text="Date/Time")
        tree_req.pack(fill="both", expand=True)

        # Pobierz wszystkie requesty z bazy
        requests = get_all_requests(self.conn)
        for row in requests:
            tree_req.insert("", tk.END, values=row)

        # Prawe okno: formularz do dodania usera na podstawie requestu
        frame_right = tk.Frame(win)
        frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame_right, text="Selected request ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(frame_right, text="New login:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Label(frame_right, text="New password:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Label(frame_right, text="Safe Comb (8xRGB):").grid(row=3, column=0, sticky="w", padx=5, pady=5)

        entry_req_id = tk.Entry(frame_right, width=20)
        entry_login = tk.Entry(frame_right, width=30)
        entry_password = tk.Entry(frame_right, width=30, show="*")
        entry_safe_comb = tk.Entry(frame_right, width=60)

        entry_req_id.grid(row=0, column=1, padx=5, pady=5)
        entry_login.grid(row=1, column=1, padx=5, pady=5)
        entry_password.grid(row=2, column=1, padx=5, pady=5)
        entry_safe_comb.grid(row=3, column=1, padx=5, pady=5)

        def on_request_select(event):
            # Gdy user wybierze wiersz z TreeView, wstawiamy ID requestu do entry_req_id
            selected = tree_req.focus()
            if not selected:
                return
            values = tree_req.item(selected, "values")  # (request_id, user_id, date_time)
            req_id = values[0]
            entry_req_id.delete(0, tk.END)
            entry_req_id.insert(0, str(req_id))

        tree_req.bind("<<TreeviewSelect>>", on_request_select)

        def on_add_user_from_request():
            req_id_str = entry_req_id.get().strip()
            new_login = entry_login.get().strip()
            new_pass = entry_password.get().strip()
            safe_str = entry_safe_comb.get().strip()

            if not req_id_str or not new_login or not new_pass or not safe_str:
                messagebox.showerror("Error", "Wypełnij wszystkie pola!")
                return

            try:
                req_id = int(req_id_str)
            except ValueError:
                messagebox.showerror("Error", "Niepoprawny Request ID.")
                return

            # Odczyt requestu z bazy, żeby poznać user_id
            all_req = get_all_requests(self.conn)
            selected_req = None
            for r in all_req:
                # r = (request_id, user_id, date_time)
                if r[0] == req_id:
                    selected_req = r
                    break

            if not selected_req:
                messagebox.showerror("Error", "Brak takiego requestu w bazie.")
                return

            requested_user_id = selected_req[1]  # user_id z wiersza w Requests

            # Wczytujemy safe_comb_list
            try:
                safe_comb_list = eval(f"[{safe_str}]")
                if len(safe_comb_list) != 8:
                    raise ValueError("Musi być dokładnie 8 krotek!")
            except Exception as e:
                messagebox.showerror("Error", f"Nieprawidłowy format Safe Combination:\n{e}")
                return

            # Dodanie usera
            add_user(self.conn, requested_user_id, new_login, new_pass, safe_comb_list)
            messagebox.showinfo("OK", f"Dodano użytkownika o ID: {requested_user_id}")

            # Usuwamy rekord z requests
            delete_request(self.conn, req_id)
            messagebox.showinfo("OK", "Rekord request został usunięty.")

            # Odświeżamy listę w drzewku
            for item in tree_req.get_children():
                tree_req.delete(item)
            updated_requests = get_all_requests(self.conn)
            for row in updated_requests:
                tree_req.insert("", tk.END, values=row)

            # Czyścimy formularz
            entry_req_id.delete(0, tk.END)
            entry_login.delete(0, tk.END)
            entry_password.delete(0, tk.END)
            entry_safe_comb.delete(0, tk.END)

        btn_add_user = tk.Button(frame_right, text="Add user from request", command=on_add_user_from_request)
        btn_add_user.grid(row=4, column=1, padx=5, pady=10, sticky="e")

    # -------------------------------------------------------
    # 4) Okno do wyświetlania i usuwania użytkowników
    # -------------------------------------------------------
    def show_users_window(self):
        win = tk.Toplevel(self)
        win.title("Users in database")

        users = get_all_users(self.conn)

        frame_top = tk.Frame(win)
        frame_top.pack(fill="both", expand=True, padx=10, pady=10)

        tree_users = ttk.Treeview(frame_top, columns=("id", "login", "password", "safe_combination"), show="headings", height=10)
        tree_users.heading("id", text="User ID")
        tree_users.heading("login", text="Login")
        tree_users.heading("password", text="Password")
        tree_users.heading("safe_combination", text="Safe Combination")

        tree_users.pack(side="left", fill="both", expand=True)

        # Dodaj pionowy scrollbar
        vsb = ttk.Scrollbar(frame_top, orient="vertical", command=tree_users.yview)
        tree_users.configure(yscroll=vsb.set)
        vsb.pack(side="right", fill="y")

        # Wstaw dane do Treeview
        for u in users:
            # u to krotka (id, login, password, safe_combination)
            tree_users.insert("", tk.END, values=u)

        # Dolna część – przycisk do usunięcia
        frame_bottom = tk.Frame(win)
        frame_bottom.pack(fill="x", padx=10, pady=10)

        def on_delete_user():
            selected = tree_users.focus()  # aktualny zaznaczony wiersz
            if not selected:
                messagebox.showwarning("Warning", "Nie wybrano żadnego użytkownika.")
                return
            values = tree_users.item(selected, "values")  # (id, login, password, safe_combination)
            user_id = values[0]

            # Potwierdzenie
            if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć użytkownika o ID '{user_id}'?"):
                delete_user(self.conn, user_id)

                # Odświeżamy listę
                tree_users.delete(*tree_users.get_children())
                new_users = get_all_users(self.conn)
                for u2 in new_users:
                    tree_users.insert("", tk.END, values=u2)

        btn_delete = tk.Button(frame_bottom, text="Delete user", command=on_delete_user)
        btn_delete.pack(side="right")

if __name__ == "__main__":
    app = App("mini-project/server/database.db")
    app.mainloop()