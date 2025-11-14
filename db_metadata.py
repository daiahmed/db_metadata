import oracledb

def connect_to_db():
    print("Welcome to Oracle Metadata Explorer!")
    print("-----------------------------------")
    username = input("Enter username: ")
    password = input("Enter password: ")
    service = input("Enter service name (default: freepdb1): ") or "freepdb1"
    host = "localhost"
    port = "8521"

    dsn = f"{host}:{port}/{service}"

    try:
        conn = oracledb.connect(user=username, password=password, dsn=dsn)
        print("\n Connected successfully!\n")
        return conn
    except Exception as e:
        print(" Connection failed:", e)
        return None


def list_objects(conn, object_type):
    cursor = conn.cursor()
    if object_type == "TABLES":
        query = "SELECT table_name FROM user_tables ORDER BY table_name"
    elif object_type == "VIEWS":
        query = "SELECT view_name FROM user_views ORDER BY view_name"
    elif object_type == "SEQUENCES":
        query = "SELECT sequence_name FROM user_sequences ORDER BY sequence_name"
    elif object_type == "USERS":
        query = "SELECT username FROM all_users ORDER BY username"
    else:
        print("Invalid type.")
        return []

    cursor.execute(query)
    results = [r[0] for r in cursor.fetchall()]
    for i, name in enumerate(results, 1):
        print(f"{i}. {name}")
    return results


def table_metadata_menu(conn, table_name):
    cursor = conn.cursor()
    while True:
        print(f"\n TABLE: {table_name}")
        print("1. Columns")
        print("2. Constraints")
        print("3. Indexes")
        print("4. Back")
        choice = input("Select metadata option: ")

        if choice == "1":
            cursor.execute("""
                SELECT column_name, data_type, data_length, nullable
                FROM user_tab_columns
                WHERE table_name = :tbl
            """, {"tbl": table_name})
            print("\nColumns:")
            for row in cursor:
                print(row)

        elif choice == "2":
            cursor.execute("""
                SELECT constraint_name, constraint_type
                FROM user_constraints
                WHERE table_name = :tbl
            """, {"tbl": table_name})
            print("\nConstraints:")
            for row in cursor:
                print(row)

        elif choice == "3":
            cursor.execute("""
                SELECT index_name, uniqueness
                FROM user_indexes
                WHERE table_name = :tbl
            """, {"tbl": table_name})
            print("\nIndexes:")
            for row in cursor:
                print(row)

        elif choice == "4":
            break
        else:
            print("Invalid option.")


def view_metadata_menu(conn, view_name):
    cursor = conn.cursor()
    while True:
        print(f"\n VIEW: {view_name}")
        print("1. Definition (SQL Text)")
        print("2. Columns")
        print("3. Back")
        choice = input("Select metadata option: ")

        if choice == "1":
            cursor.execute("""
                SELECT text FROM user_views WHERE view_name = :v
            """, {"v": view_name})
            text = cursor.fetchone()
            print("\nView Definition:\n", text[0] if text else "No definition found.")

        elif choice == "2":
            cursor.execute("""
                SELECT column_name, data_type, data_length, nullable
                FROM user_tab_columns
                WHERE table_name = :v
            """, {"v": view_name})
            print("\nColumns:")
            for row in cursor:
                print(row)

        elif choice == "3":
            break
        else:
            print("Invalid option.")


def sequence_metadata_menu(conn, seq_name):
    cursor = conn.cursor()
    while True:
        print(f"\n SEQUENCE: {seq_name}")
        print("1. Properties")
        print("2. Back")
        choice = input("Select metadata option: ")

        if choice == "1":
            cursor.execute("""
                SELECT min_value, max_value, increment_by, cycle_flag, order_flag, last_number
                FROM user_sequences
                WHERE sequence_name = :seq
            """, {"seq": seq_name})
            seq = cursor.fetchone()
            if seq:
                print(f"\nMin Value: {seq[0]}")
                print(f"Max Value: {seq[1]}")
                print(f"Increment By: {seq[2]}")
                print(f"Cycle: {seq[3]}")
                print(f"Order: {seq[4]}")
                print(f"Last Number: {seq[5]}")
            else:
                print("Sequence not found.")
        elif choice == "2":
            break
        else:
            print("Invalid option.")


def user_metadata_menu(conn, username):
    cursor = conn.cursor()
    while True:
        print(f"\n USER: {username}")
        print("1. Account Info")
        print("2. Roles")
        print("3. Privileges")
        print("4. Back")
        choice = input("Select metadata option: ")

        if choice == "1":
            cursor.execute("""
                SELECT username, account_status, created, default_tablespace, temporary_tablespace
                FROM all_users
                WHERE username = :u
            """, {"u": username})
            info = cursor.fetchone()
            if info:
                print("\nAccount Info:")
                print(f"Username: {info[0]}")
                print(f"Status: {info[1]}")
                print(f"Created: {info[2]}")
                print(f"Default Tablespace: {info[3]}")
                print(f"Temporary Tablespace: {info[4]}")
            else:
                print("User not found.")

        elif choice == "2":
            cursor.execute("""
                SELECT granted_role FROM dba_role_privs WHERE grantee = :u
            """, {"u": username})
            print("\nRoles:")
            for row in cursor:
                print(row)

        elif choice == "3":
            cursor.execute("""
                SELECT privilege FROM dba_sys_privs WHERE grantee = :u
            """, {"u": username})
            print("\nSystem Privileges:")
            for row in cursor:
                print(row)

        elif choice == "4":
            break
        else:
            print("Invalid option.")


# ===== Main Menu =====

def main():
    conn = connect_to_db()
    if not conn:
        return

    while True:
        print("Select the object type you want to view:")
        print("1. Tables")
        print("2. Views")
        print("3. Sequences")
        print("4. Users")
        print("5. Exit")
        option = input("Enter option number: ")

        if option == "5":
            print("Exiting... ")
            break

        types = {"1": "TABLES", "2": "VIEWS", "3": "SEQUENCES", "4": "USERS"}
        obj_type = types.get(option)
        if not obj_type:
            print("Invalid selection.\n")
            continue

        objects = list_objects(conn, obj_type)
        if not objects:
            print(f"No {obj_type.lower()} found.\n")
            continue

        num = input(f"\nSelect a {obj_type[:-1].lower()} number: ")
        try:
            obj_name = objects[int(num) - 1]
            if obj_type == "TABLES":
                table_metadata_menu(conn, obj_name)
            elif obj_type == "VIEWS":
                view_metadata_menu(conn, obj_name)
            elif obj_type == "SEQUENCES":
                sequence_metadata_menu(conn, obj_name)
            elif obj_type == "USERS":
                user_metadata_menu(conn, obj_name)
        except Exception as e:
            print("Invalid selection or error:", e)

    conn.close()


if __name__ == "__main__":
    main()


##username = "system"
#password = "SysPassword1"
#dsn = "localhost:8521/freepdb1"
#docker ps
#>docker start oracle-23ai
#docker logs oracle-23ai //database ready to use