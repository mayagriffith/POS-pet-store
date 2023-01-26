#DATABASE PROJECT BY MAYA AND LAUREN
#A PET COSTUME STORE!!!
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker



# Establish connection
conn = sqlite3.connect('Pet Fashion.db')
cur = conn.cursor()

#LOGIN FUNCTION
def newCus():
    new = input("Are you a new customer?  (y/n) ")
    if new == "y":
        #find number of last customer id
        all_customers = cur.execute("SELECT CustomerID from Customers;").fetchall()
        for j, i in enumerate(all_customers):
            newCusID = all_customers[j][0]
        newCusID = int(newCusID) + 1
        name = input("What is your full name?   ")
        email = input("What is your email?  ")
        print("You are now Customer number " + str(newCusID) + ". Please remeber that to login.\n")
        #add to database
        cur.execute("INSERT INTO Customers (Name,CustomerID,EmailAddress) VALUES (?,?,?);", (name, newCusID, email))
        conn.commit()
    else:
        print("Please login with your customer ID. It should be a number.\n")


#LOGIN FUNCTION
def login():
    all_customers = cur.execute("SELECT CustomerID from Customers;").fetchall()
    customer_id = input("Enter Customer ID: ")

    # Validate customer ID
    while customer_id not in all_customers.__str__():
        print("Customer ID not found.")
        customer_id = input("Please enter a valid customer ID: ")
    
    return customer_id


# Create an order
def place_order(customer_id):

    all_items = cur.execute("SELECT ItemNumber from Inventory;").fetchall()
    all_itemname = cur.execute("SELECT Item, Price from Inventory;").fetchall()
    for j, i in enumerate(all_itemname):
        num = '{}. '.format(all_items[j][0])
        item = '{}'.format(all_itemname[j][0])
        price = '  ${}'.format(all_itemname[j][1])
        print (num, item, price)

    item_number = input("Enter the item number: ")

    # Validate item number
    while item_number not in all_items.__str__():
        print("Item number not found.")
        item_number = input("Please enter a valid item number: ")

    # Get item name and cost
    item_purchased = cur.execute("SELECT Item FROM Inventory WHERE ItemNumber = ?", (item_number,)).fetchone()
    item_purchased = item_purchased[0]
    total_cost = cur.execute("SELECT Price FROM Inventory WHERE ItemNumber = ?", (item_number,)).fetchone()
    total_cost = total_cost[0]

    # Assign order number
    orders = cur.execute("SELECT count(OrderNumber) FROM Orders").fetchone()
    orders = orders[0]
    order_number = "O" + str((orders+1))

    # Insert into Orders
    cur.execute("INSERT INTO Orders (CustomerID,TotalCost,OrderNumber,ItemPurchased) VALUES (?,?,?,?);", (customer_id, total_cost, order_number, item_number,))
    conn.commit()

    #DELETE ONE FROM INVENTORY WHEN AN ORDER IS PLACED
    cur.execute("UPDATE Inventory SET Quantity = (Quantity - 1) WHERE ItemNumber = ?;", (item_number,))
    conn.commit()

    # Validate
    check = cur.execute("SELECT * FROM Orders WHERE OrderNumber = ?", (order_number,)).fetchall()
    print(check)
    print("Order successfully placed!")
    #Join with Inventory to get name of item too
    thisprice = cur.execute("SELECT Orders.totalCost, Inventory.Item FROM Orders JOIN Inventory ON Orders.ItemPurchased=Inventory.ItemNumber WHERE Orders.OrderNumber = ?", (order_number,)).fetchall()
    cost = '{}'.format(thisprice[0][0])
    itemName = '{}'.format(thisprice[0][1])
    print("You have ordered a " + itemName + " for $" + cost)


# calculate money spent
# search up order number or name
# USE JOIN FOR JOIN CUSTOMERS AND ORDERS, COUNT HOW MANY ORDERS A CUSTOMBER HAS MADE
def lookup_orders(customer_id):
    #how many orders has a user made, total up all the orders
    #get all the ordernumbers of the customer
    cust_orders = cur.execute("SELECT OrderNumber from Orders WHERE CustomerId = ?;", (customer_id,)).fetchall()
    cust_prices = cur.execute("SELECT TotalCost from Orders WHERE CustomerId = ?;", (customer_id,)).fetchall()

    #get the customer name
    cust_name = cur.execute("SELECT Customers.Name FROM Customers JOIN Orders ON Orders.CustomerID=Customers.CustomerID WHERE Orders.CustomerId = ? ;", (customer_id,)).fetchone()
    name = '{}'.format(cust_name[0])
    print("\nHello, " + name)

    #get total price of all items and number
    totalprices = [i[0] for i in cust_prices]
    total = 0;
    totalitems = 0

    for count, i in enumerate(totalprices):
        total+=i
        totalitems = count + 1

    print("You ordered " + str(totalitems) + " items.The total of your orders is: $" + str(total))

    cust_products = cur.execute("SELECT Inventory.Item FROM Inventory JOIN Orders ON Orders.ItemPurchased=Inventory.ItemNumber WHERE Orders.CustomerId = ? ;", (customer_id,)).fetchall()
    print("Order Number Product Price")
    for i, prods in enumerate(cust_products):
        prod = '{}'.format(cust_products[i][0])
        num = i+1
        ornum = '{}'.format(cust_orders[i][0])
        price = '{}'.format(cust_prices[i][0])
        print(str(num) + ". " + ornum + " " + prod + " $" + price)

    where_query = input("\nWould you like to look up a specific order?    (y/n)   ")
    if where_query == "y":
        print("Find an order based on: ")
        print("- CustomerID")
        print("- OrderNumber")
        print("- ItemPurchased")
        print("- TotalCost")

        col_choice = input("Enter a column to search: ")
        search_val = input("Enter the value to find: ")

        spec_order = cur.execute("SELECT * FROM Orders WHERE {} = ?;".format(col_choice), (search_val,)).fetchall()
        orders_df = pd.DataFrame(data=spec_order, index=None, columns=['CustomerID','TotalCost','OrderNumber','ItemPurchased'])
        print(orders_df.to_string(index=False) + "\n")

    stats = input("Would you like to calculate stats for your orders?   (y/n)   ")
    if stats == "y":
        #calculate mean
        mean = cur.execute("SELECT avg(totalCost) FROM Orders WHERE CustomerId = ? ;", (customer_id,)).fetchall()
        meanstr = '{}'.format(mean[0][0])
        print("Mean: $"+ meanstr)
        #calculate min
        min = cur.execute("SELECT MIN(totalCost) FROM Orders WHERE CustomerId = ? ;", (customer_id,)).fetchall()
        minstr = '{}'.format(min[0][0])
        print("Min: $"+ minstr)
        #calculate max
        max = cur.execute("SELECT MAX(totalCost) FROM Orders WHERE CustomerId = ? ;", (customer_id,)).fetchall()
        maxstr = '{}'.format(max[0][0])
        print("Max: $"+ maxstr)
        #calculate median
        med = cur.execute("SELECT TotalCost FROM Orders WHERE CustomerID = ? ORDER BY TotalCost ASC LIMIT 1 OFFSET (SELECT COUNT(TotalCost)/2 FROM Orders WHERE CustomerID = ?);", (customer_id,customer_id,)).fetchall()
        medstr = '{}'.format(med[0][0])
        print("Median: $"+ medstr)
    else:
        print("Thanks for looking at your orders.\n")


# can modify or delete an order
def change_order(customer_id):
    lookup_orders(customer_id)
    # get orders made by specific user
    cust_orders = cur.execute("SELECT OrderNumber from Orders WHERE CustomerId = ?;", (customer_id,)).fetchall()
    order_number = input("\nEnter order number to delete/modify: ")

    # Validate order for user
    while order_number not in cust_orders.__str__():
        print("Order number not found.")
        order_number = input("Please enter a valid order number: ")

    # Verify order is found yay
    print("\nFound Order #" + order_number)
    order = cur.execute("SELECT * FROM Orders WHERE OrderNumber = ?", (order_number,)).fetchall()
    print(order)

    # Get user choice
    mod = input("Do you want to 'modify' or 'delete' Order #" + order_number + "? ")
    
    # modify
    if "modify" in mod.__str__():
        print("\nAvaliable Columns: \n- CustomerID \n- TotalCost \n- OrderNumber \n- ItemPurchased")
        col_choice = input("\nWhich column would you like to edit? ")

        # get updated value
        new_val = input("Enter new value: ")

        # actually update
        cur.execute("UPDATE Orders SET {} = ? WHERE OrderNumber = ?;".format(col_choice), (new_val, order_number,))
        conn.commit()  
        print("Updated!") 

        # verify updated
        verify = cur.execute("SELECT * FROM Orders WHERE OrderNumber = ?", (order_number,)).fetchall()
        print(verify)

    # delete
    if "delete" == mod.__str__():
        choice = input("Are you sure you want to delete this order? (y/n) ")

        if choice == "y":
            cur.execute("DELETE FROM Orders WHERE OrderNumber = ?;", (order_number,))
            conn.commit()
            print("Deleted successfully!")
        if choice == "n":
            menu()


def plot():
    #PLOT OF customer vs number of items ordered or how expensive the items are... bar chart
    # TODO: write into df, plot using pandas?
    typeofplot = input("Would you like to know \n 1) How many orders each customer has \n 2) How popular each product is \n")

    if typeofplot == "1":
        #PLOT SHOWING HOW MANY ORDERS EACH CUSTOMER HAS
        plot = pd.read_sql_query("SELECT CustomerID as 'Customer', COUNT(CustomerID) as 'Orders' FROM Orders GROUP BY CustomerID;", conn)
        print(plot)
        plot.plot(x='Customer', y='Orders', kind='bar')
        plt.title('Orders Placed by Each Customer')
        plt.show()
    #PLOT SHOWING WHAT PRODUCT IS MOST POPULAR
    else:
        plot = pd.read_sql_query("SELECT ItemPurchased as 'Item Number', COUNT(ItemPurchased) as 'Number of Orders' FROM Orders GROUP BY ItemPurchased;", conn)
        plot.plot(kind='scatter',x='Item Number',y='Number of Orders',color='red')
        # use axis={'both', 'x', 'y'} to choose axis
        plt.locator_params(axis="both", integer=True, tight=True)
        plt.title('Orders Per Item')
        plt.show()


def menu(customer_id):
    # print options
    stop = False
    while stop == False:

        print("\n1. Add an order")
        print("2. Modify/Delete an order")
        print("3. Lookup your orders")
        print("4. Lookup Data")
        print("5. Quit")

        # ask user what to do
        choice = input("Please pick a choice 1-5: ")


        # call appropriate function
        if choice == "1":
            place_order(customer_id)
        elif choice == "2" :
            change_order(customer_id)
        elif choice == "3":
            lookup_orders(customer_id)
        elif choice == "4":
            plot()
        elif choice == "5":
            stop = True
        else:
            print("Not valid.")


def main():
    print("Welcome to the fanciest pet store you wil ever visit! ")
    newCus()
    user = login()
    menu(user)

main()



conn.close()