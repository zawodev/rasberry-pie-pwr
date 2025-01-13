import sqlite3
from datetime import datetime
import json  # do serializacji safe_combination

# =================================
# Funkcje pomocnicze
# =================================

def create_connection(db_file: str):
    """
    Tworzy i zwraca połączenie do bazy danych SQLite.
    Jeśli nie istnieje plik db_file, zostanie on utworzony.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Połączono z bazą danych:", db_file)

        # Włączenie wsparcia dla kluczy obcych (domyślnie w SQLite jest wyłączone)
        conn.execute("PRAGMA foreign_keys = ON;")

    except sqlite3.Error as e:
        print("Błąd podczas łączenia z bazą danych:", e)
    return conn

def create_tables(conn):
    """
    Tworzy tabele w bazie danych, jeśli jeszcze nie istnieją.
    Uwaga: user_id w tabeli Users jest typu TEXT, a w Ewidencja/Requests klucz obcy też jest TEXT.
    """
    try:
        cursor = conn.cursor()

        
        create_users_table = """
        CREATE TABLE IF NOT EXISTS Users (
            id TEXT PRIMARY KEY,
            login TEXT NOT NULL,
            password TEXT NOT NULL,
            safe_combination TEXT
        );
        """
        cursor.execute(create_users_table)

        
        create_login_records_table = """
        CREATE TABLE IF NOT EXISTS LoginRecords (
            login_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date_time TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        );
        """
        cursor.execute(create_login_records_table)

        
        create_requests_table = """
        CREATE TABLE IF NOT EXISTS Requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date_time TEXT NOT NULL
        );
        """
        cursor.execute(create_requests_table)

        conn.commit()
        print("Tabele zostały utworzone (lub już istniały).")
    except sqlite3.Error as e:
        print("Błąd podczas tworzenia tabel:", e)


# =================================
# Operacje CRUD na tabeli Users
# =================================

def add_user(conn, user_id: str, login: str, password: str, safe_combination: list):
    """
    Dodaje nowego użytkownika do tabeli Users.
    user_id: tekstowe ID użytkownika (np. numer karty, unikalny login)
    safe_combination: lista ośmiu 3-elementowych krotek (RGB), np. [(255,0,0), (128,128,128), ...].
    """
    try:
        cursor = conn.cursor()

        # Serializujemy safe_combination do JSON,
        # np. [(255, 0, 0), (0, 255, 0), ...] -> "[[255, 0, 0], [0, 255, 0], ...]"
        safe_combination_json = json.dumps(safe_combination)

        query = """
        INSERT INTO Users (id, login, password, safe_combination)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (user_id, login, password, safe_combination_json))
        conn.commit()
        print(f"Dodano użytkownika: {user_id} (login: {login})")
    except sqlite3.Error as e:
        print("Błąd podczas dodawania użytkownika:", e)

def get_user_by_id(conn, user_id: str):
    """
    Pobiera użytkownika z tabeli Users po ID (typ TEXT).
    Zwraca słownik z danymi lub None, jeśli nie ma takiego użytkownika.
    """
    try:
        cursor = conn.cursor()
        query = "SELECT id, login, password, safe_combination FROM Users WHERE id = ?"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        if row:
            # Odczytujemy safe_combination z JSON
            safe_combination = json.loads(row[3]) if row[3] else None
            return {
                'id': row[0],
                'login': row[1],
                'password': row[2],
                'safe_combination': safe_combination
            }
        return None
    except sqlite3.Error as e:
        print("Błąd podczas pobierania użytkownika:", e)
        return None
    
def get_all_users(conn):
    """
    Zwraca listę krotek (id, login, password, safe_combination) wszystkich użytkowników.
    """
    try:
        cursor = conn.cursor()
        query = "SELECT id, login, password, safe_combination FROM Users"
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(e)
        return []

def update_user_password(conn, user_id: str, new_password: str):
    """
    Aktualizuje hasło użytkownika (po ID typu TEXT).
    """
    try:
        cursor = conn.cursor()
        query = """
        UPDATE Users
        SET password = ?
        WHERE id = ?
        """
        cursor.execute(query, (new_password, user_id))
        conn.commit()
        print(f"Zaktualizowano hasło użytkownika ID = {user_id}.")
    except sqlite3.Error as e:
        print("Błąd podczas aktualizacji hasła:", e)

def delete_user(conn, user_id: str):
    """
    Usuwa użytkownika z tabeli Users po ID (TEXT).
    Bez ON DELETE CASCADE w definicji kluczy obcych, nie usunie powiązanych wpisów w Ewidencja/Requests.
    """
    try:
        cursor = conn.cursor()
        query = "DELETE FROM Users WHERE id = ?"
        cursor.execute(query, (user_id,))
        conn.commit()
        print(f"Usunięto użytkownika ID = {user_id}.")
    except sqlite3.Error as e:
        print("Błąd podczas usuwania użytkownika:", e)

# =================================
# Operacje CRUD na tabeli LoginRecords
# =================================

def add_login_record(conn, user_id: str, status: str):
    """
    Dodaje wpis do tabeli LoginRecords.
    Wstawiamy aktualną datę/czas w polu date_time.
    user_id: tekstowe ID użytkownika (powiązane z Users.id)
    status: np. "CHECK_IN", "CHECK_OUT", itp.
    """
    try:
        cursor = conn.cursor()
        now = datetime.now().isoformat(timespec='seconds')  # np. '2025-01-12T13:01:00'
        query = """
        INSERT INTO LoginRecords (user_id, date_time, status)
        VALUES (?, ?, ?)
        """
        cursor.execute(query, (user_id, now, status))
        conn.commit()
        print(f"Dodano wpis do LoginRecords z user_id = {user_id}, status = {status}")
    except sqlite3.Error as e:
        print("Błąd podczas dodawania wpisu do LoginRecords:", e)

def get_all_login_records(conn):
    """
    Pobiera wszystkie wpisy z tabeli LoginRecords.
    Zwraca listę krotek (login_record_id, user_id, date_time, status) lub pustą listę.
    """
    try:
        cursor = conn.cursor()
        query = "SELECT login_record_id, user_id, date_time, status FROM LoginRecords"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print("Błąd podczas pobierania danych z LoginRecords:", e)
        return []

# =================================
# Operacje CRUD na tabeli Requests
# =================================

def add_request(conn, user_id: str):
    """
    Dodaje wpis do tabeli Requests.
    Wstawiamy aktualną datę/czas w polu date_time.
    user_id: tekstowe ID użytkownika (powiązane z Users.id)
    """
    try:
        cursor = conn.cursor()
        now = datetime.now().isoformat(timespec='seconds')
        query = """
        INSERT INTO Requests (user_id, date_time)
        VALUES (?, ?)
        """
        cursor.execute(query, (user_id, now))
        conn.commit()
        print(f"Dodano wpis do Requests z user_id = {user_id}")
    except sqlite3.Error as e:
        print("Błąd podczas dodawania wpisu do Requests:", e)

def get_all_requests(conn):
    """
    Pobiera wszystkie wpisy z tabeli Requests.
    Zwraca listę krotek (request_id, user_id, date_time) lub pustą listę.
    """
    try:
        cursor = conn.cursor()
        query = "SELECT request_id, user_id, date_time FROM Requests"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print("Błąd podczas pobierania danych z Requests:", e)
        return []
    
def delete_request(conn, request_id: int):
    """
    Usuwa rekord z tabeli Requests po request_id.
    """
    try:
        cursor = conn.cursor()
        query = "DELETE FROM Requests WHERE request_id = ?"
        cursor.execute(query, (request_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

# =================================
# Główny blok wykonywalny (przykład użycia)
# =================================

if __name__ == "__main__":
    # Połączenie z bazą (lub utworzenie nowego pliku DB)
    connection = create_connection("mini-project/server/database.db")

    if connection:
        # Tworzenie tabel (jeśli jeszcze nie istnieją)
        create_tables(connection)

        # Przykład dodania użytkownika z tekstowym user_id
        user_id_example = "CARD_001"
        user_login = "jan_kowalski"
        user_password = "haslo123"

        # Kombinacja sejfu to lista ośmiu 3-elementowych krotek RGB (np. same zera i jedynki dla uproszczenia):
        # [(R1,G1,B1), (R2,G2,B2), ..., (R8,G8,B8)]
        user_safe_combination = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (128, 128, 128),
            (255, 255, 0),
            (255, 165, 0),
            (0, 255, 255),
            (255, 0, 255)
        ]

        # Dodanie użytkownika
        add_user(connection, user_id_example, user_login, user_password, user_safe_combination)

        # Pobranie użytkownika
        user = get_user_by_id(connection, user_id_example)
        print("Pobrany użytkownik:", user)

        # Aktualizacja hasła
        update_user_password(connection, user_id_example, "noweHaslo456")

        # Dodanie wpisu do Ewidencja (np. check-in)
        add_login_record(connection, user_id_example, "CHECK_IN")

        # Dodanie wpisu do Requests
        add_request(connection, "CARD_002")

        # Odczyt wszystkich wpisów z Ewidencja
        login_record_rows = get_all_login_records(connection)
        print("Wszystkie wpisy Ewidencja:")
        for row in login_record_rows:
            print(row)

        # Odczyt wszystkich wpisów z Requests
        requests_rows = get_all_requests(connection)
        print("Wszystkie wpisy Requests:")
        for row in requests_rows:
            print(row)

        # Przykład usunięcia użytkownika
        # delete_user(connection, user_id_example)

        # Zamknięcie połączenia
        connection.close()
