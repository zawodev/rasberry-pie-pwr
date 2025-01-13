from database import (
    create_connection,
    create_tables,
    add_user,
    get_all_login_records,
    get_all_requests,
    delete_request,
    get_all_users,
    delete_user
)
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

class App(tk.Tk):
    def __init__(self, db_path="mini-project/server/database.db"):
        super().__init__()
        self.title("GUI Admin App")

        # Połączenie z bazą i utworzenie tabel
        self.conn = create_connection(db_path)
        if self.conn:
            create_tables(self.conn)

        # Etykieta tytułowa
        label = tk.Label(self, text="Menu główne", font=("Arial", 16, "bold"))
        label.pack(pady=20)

        # 1) Przycisk: Wyświetlenie i usuwanie użytkowników
        btn_show_users = tk.Button(self, text="Pokaż użytkowników", width=20, command=self.show_users_window)
        btn_show_users.pack(pady=5)

        # 2) Przycisk: Dodanie nowego użytkownika
        btn_new_user = tk.Button(self, text="Dodaj nowego użytkownika", width=20, command=self.show_add_user_window)
        btn_new_user.pack(pady=5)

        # 3) Przycisk: Wyświetlenie ewidencji
        btn_login_record = tk.Button(self, text="Pokaż ewidencję logowań", width=20, command=self.show_login_record_window)
        btn_login_record.pack(pady=5)

        # 4) Przycisk: Obróbka (Process) Requests
        btn_requests = tk.Button(self, text="Pokaż prośby o rejestrację", width=20, command=self.show_requests_window)
        btn_requests.pack(pady=5)

    # -------------------------------------------------------
    # 1) Okno do dodawania nowego użytkownika
    # -------------------------------------------------------
    def show_add_user_window(self):
        win = tk.Toplevel(self)
        win.title("Dodaj nowego użytkownika")

        tk.Label(win, text="ID Użytkownika (ID karty):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(win, text="Login:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Label(win, text="Hasło:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Label(win, text="Kombinacja sejfu (8 liczb 0..255):").grid(row=3, column=0, sticky="w", padx=5, pady=5)

        entry_user_id = tk.Entry(win, width=30)
        entry_login = tk.Entry(win, width=30)
        entry_password = tk.Entry(win, show="*", width=30)

        entry_user_id.grid(row=0, column=1, padx=5, pady=5)
        entry_login.grid(row=1, column=1, padx=5, pady=5)
        entry_password.grid(row=2, column=1, padx=5, pady=5)

        # Ramka na 8 pól z wartościami 0..255
        frame_safe = tk.Frame(win)
        frame_safe.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Przygotujemy listę (entry_safe_list) i dla każdego elementu dodamy Entry + przycisk
        entry_safe_list = []
        for i in range(8):
            sub_frame = tk.Frame(frame_safe)
            sub_frame.pack(side="top", anchor="w")

            lbl_i = tk.Label(sub_frame, text=f"{i+1}.")
            lbl_i.pack(side="left")

            e = tk.Entry(sub_frame, width=5)
            e.pack(side="left", padx=3)
            entry_safe_list.append(e)

            # Przycisk do color pickera
            def pick_color_factory(entry_widget=e):
                def pick_color():
                    color_code = colorchooser.askcolor(title="Wybierz kolor")
                    if color_code and color_code[0]:
                        # color_code to ((R, G, B), '#rrggbb')
                        r, g, b = color_code[0]
                        # Konwersja np. do skali szarości
                        gray = int((r + g + b) // 3)
                        entry_widget.delete(0, tk.END)
                        entry_widget.insert(0, str(gray))
                return pick_color

            btn_color = tk.Button(sub_frame, text="Kolor", command=pick_color_factory(e))
            btn_color.pack(side="left", padx=2)

        def on_add():
            user_id = entry_user_id.get().strip()
            login = entry_login.get().strip()
            password = entry_password.get().strip()

            if not user_id or not login or not password:
                messagebox.showerror("Error", "Uzupełnij wszystkie pola: ID, Login, Hasło.")
                return

            # Odczytujemy 8 liczb z entry
            safe_comb_values = []
            for i, e in enumerate(entry_safe_list):
                val_str = e.get().strip()
                if not val_str:
                    messagebox.showerror("Error", f"Brak wartości dla pola nr {i+1}.")
                    return
                try:
                    val_int = int(val_str)
                except ValueError:
                    messagebox.showerror("Error", f"Niepoprawna liczba w polu nr {i+1}: '{val_str}'")
                    return
                if not (0 <= val_int <= 255):
                    messagebox.showerror("Error", f"Wartość w polu nr {i+1} musi być w zakresie 0..255.")
                    return
                safe_comb_values.append(val_int)

            if len(safe_comb_values) != 8:
                messagebox.showerror("Error", "Musisz podać dokładnie 8 liczb (0..255).")
                return

            # Dodanie do bazy
            add_user(self.conn, user_id, login, password, safe_comb_values)
            messagebox.showinfo("OK", f"Dodano nowego użytkownika: {user_id}")
            win.destroy()

        btn_save = tk.Button(win, text="Dodaj", command=on_add)
        btn_save.grid(row=4, column=1, pady=10, sticky="e")

    # -------------------------------------------------------
    # 2) Okno wyświetlające login_record (Ewidencja)
    # -------------------------------------------------------
    def show_login_record_window(self):
        win = tk.Toplevel(self)
        win.title("Ewidencja logowań")

        records = get_all_login_records(self.conn)

        tree = ttk.Treeview(win, columns=("login_record_id", "user_id", "date_time", "status"), show="headings")
        tree.heading("login_record_id", text="Login Record ID")
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
        win.title("Prośby o rejestrację")

        # Lewe okno: lista requestów
        frame_left = tk.Frame(win)
        frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame_left, text="Lista próśb:").pack(anchor="w")

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

        tk.Label(frame_right, text="Wybrane ID (Request ID):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(frame_right, text="Login:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Label(frame_right, text="Hasło:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        tk.Label(frame_right, text="Kombinacja (8 liczb 0..255):").grid(row=3, column=0, sticky="w", padx=5, pady=5)

        entry_req_id = tk.Entry(frame_right, width=20)
        entry_login = tk.Entry(frame_right, width=30)
        entry_password = tk.Entry(frame_right, width=30, show="*")

        entry_req_id.grid(row=0, column=1, padx=5, pady=5)
        entry_login.grid(row=1, column=1, padx=5, pady=5)
        entry_password.grid(row=2, column=1, padx=5, pady=5)

        # Ramka z 8 polami
        frame_right_safe = tk.Frame(frame_right)
        frame_right_safe.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        entry_req_safe_list = []
        for i in range(8):
            sub_frame = tk.Frame(frame_right_safe)
            sub_frame.pack(side="top", anchor="w")

            lbl_i = tk.Label(sub_frame, text=f"{i+1}.")
            lbl_i.pack(side="left")

            e = tk.Entry(sub_frame, width=5)
            e.pack(side="left", padx=3)
            entry_req_safe_list.append(e)

            # Przycisk do color pickera
            def pick_color_factory(entry_widget=e):
                def pick_color():
                    color_code = colorchooser.askcolor(title="Wybierz kolor")
                    if color_code and color_code[0]:
                        r, g, b = color_code[0]
                        gray = int((r + g + b) // 3)
                        entry_widget.delete(0, tk.END)
                        entry_widget.insert(0, str(gray))
                return pick_color

            btn_color = tk.Button(sub_frame, text="Kolor", command=pick_color_factory(e))
            btn_color.pack(side="left", padx=2)

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

            if not req_id_str or not new_login or not new_pass:
                messagebox.showerror("Error", "Wypełnij pola Request ID, Login, Hasło.")
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

            # Zbierzmy 8 liczb
            safe_comb_values = []
            for i, e in enumerate(entry_req_safe_list):
                val_str = e.get().strip()
                if not val_str:
                    messagebox.showerror("Error", f"Brak wartości w polu nr {i+1}.")
                    return
                try:
                    val_int = int(val_str)
                except ValueError:
                    messagebox.showerror("Error", f"Niepoprawna liczba w polu nr {i+1}: '{val_str}'")
                    return
                if not (0 <= val_int <= 255):
                    messagebox.showerror("Error", f"Wartość w polu nr {i+1} musi być w zakresie 0..255.")
                    return
                safe_comb_values.append(val_int)

            if len(safe_comb_values) != 8:
                messagebox.showerror("Error", "Musisz podać dokładnie 8 liczb (0..255).")
                return

            # Dodanie usera
            add_user(self.conn, requested_user_id, new_login, new_pass, safe_comb_values)
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
            for e in entry_req_safe_list:
                e.delete(0, tk.END)

        btn_add_user = tk.Button(frame_right, text="Dodaj", command=on_add_user_from_request)
        btn_add_user.grid(row=4, column=1, padx=5, pady=10, sticky="e")

    # -------------------------------------------------------
    # 4) Okno do wyświetlania i usuwania użytkowników
    # -------------------------------------------------------
    def show_users_window(self):
        win = tk.Toplevel(self)
        win.title("Lista Użytkowników")

        users = get_all_users(self.conn)

        frame_top = tk.Frame(win)
        frame_top.pack(fill="both", expand=True, padx=10, pady=10)

        tree_users = ttk.Treeview(frame_top, columns=("id", "login", "password", "safe_combination"), show="headings", height=10)
        tree_users.heading("id", text="ID")
        tree_users.heading("login", text="Login")
        tree_users.heading("password", text="Hasło")
        tree_users.heading("safe_combination", text="Kombinacja (JSON)")

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

        btn_delete = tk.Button(frame_bottom, text="Usuń", command=on_delete_user)
        btn_delete.pack(side="right")


if __name__ == "__main__":
    app = App("mini-project/server/database.db")
    app.mainloop()
