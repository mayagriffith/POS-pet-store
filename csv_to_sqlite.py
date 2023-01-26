import sqlite3
import pandas as pd

def csv_to_sql():
    # Create DB, establish connected to DB
    conn = sqlite3.connect('Pet Fashion.db')
    cur = conn.cursor()

    # CUSTOMERS

    # Create Customers table
    cur.execute("DROP TABLE IF EXISTS Customers;")
    cur.execute("CREATE TABLE Customers ('Name',CustomerID,'EmailAddress')")

    # Read from Customers
    customers = pd.read_csv('data/Pet Fashion DB - Customers.csv')
    customers.to_sql('Customers', conn, if_exists='replace', index=False)

    # Fetch
    result = cur.execute("SELECT * FROM Customers;").fetchall()
    # print(result)

    # Read into DF
    customers_df = pd.read_sql_query("SELECT * FROM Customers", conn)

    # INVENTORY

    # Create posts table
    cur.execute("DROP TABLE IF EXISTS Inventory;")
    cur.execute("CREATE TABLE Inventory ('Item',ItemNumber,Quantity,Price);")

    # Read from Inventory
    inventory = pd.read_csv('data/Pet Fashion DB - Inventory.csv')
    inventory.to_sql('Inventory', conn, if_exists='replace', index=False)

    # Fetch
    result = cur.execute("SELECT * FROM Inventory;").fetchall()
    print(result)

    # Read into DF
    inventory_df = pd.read_sql_query("SELECT * FROM Inventory;", conn)

    # ORDERS

    # Create Orders table
    cur.execute("DROP TABLE IF EXISTS Orders;")
    cur.execute("CREATE TABLE Orders (CustomerID,TotalCost,'OrderNumber','ItemPurchased');")

    # Read from Orders
    orders = pd.read_csv('data/Pet Fashion DB - Orders.csv')
    orders.to_sql('Orders', conn, if_exists='replace', index=False)

    # Fetch
    result = cur.execute("SELECT * FROM Orders;").fetchall()
    # print(result)

    # Commit
    conn.commit()

    # Close connection
    conn.close()

csv_to_sql()