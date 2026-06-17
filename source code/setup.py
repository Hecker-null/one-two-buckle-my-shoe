
import importlib.util
import subprocess
import sys

packages = {
    "customtkinter": "customtkinter",
    "mysql.connector": "mysql-connector-python",
    "reportlab": "reportlab"
}

for module_name, pip_name in packages.items():
    if importlib.util.find_spec(module_name):
        print(f"{pip_name} already installed")
    else:
        print(f"Installing {pip_name}...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name],
            check=True
        )
import time
import mysql.connector as mysql

username=input("enter your mysql username: ").strip()
password=input("Enter your mysql root password: ").strip()


try:
    con=mysql.connect(
        host="localhost",
        password=password,
        user=username
    )
    
    cur=con.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS GST")
    cur.execute("USE GST")
    
    #create users
    cur.execute("""CREATE TABLE IF NOT EXISTS USERS(
                GSTIN VARCHAR(20) PRIMARY KEY,
                Bname VARCHAR(20),
                Password VARCHAR(20))""")
    #create invoices
    cur.execute("""CREATE TABLE IF NOT EXISTS INVOICES(
                invoice_id int AUTO_INCREMENT primary key, 
                GSTIN VARCHAR(20) NOT NULL,
                BADDR VARCHAR(200),
                BPHN VARCHAR(20),
                INVOICE_DATE DATE,
                CNAME VARCHAR(20),
                CPHN VARCHAR(20),
                CADDR VARCHAR(200),
                SUBTOTAL FLOAT,
                GRAND_TOTAL FLOAT)""")
    #create items
    cur.execute("""CREATE TABLE IF NOT EXISTS ITEMS(
                INVOICE_ID INT,
                ITEM_NAME VARCHAR(20),
                COST FLOAT,
                GST INT,
                QUANTITY INT,
                AMOUNT FLOAT,
                AMOUNT_GST FLOAT)""")
    con.commit()
    cur.close()
    con.close()
    #save password given by the user
    with open("config.txt", "w") as f:
        f.write(f"mysql_user={username}\n")
        f.write(f"mysql_password={password}")
    
    print("Creating tables.....")
    time.sleep(2)
    print("Almost there........")
    time.sleep(4)
    print("ALL DONE.....")
except mysql.Error as e:
    print("setup failed")
    print(e)
    
