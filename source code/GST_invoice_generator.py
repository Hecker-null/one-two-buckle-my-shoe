#IMPORT LIBRARIES
import customtkinter as ctk
import mysql.connector as mysql
from tkinter import messagebox,filedialog
from tkinter import ttk
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table,TableStyle
#make the accsess to old invoices possible
#also add a invoice id search
#also add the ability to delete the invoices selected 
config = {}

with open("config.txt", "r") as f:
    for line in f:
        key, value = line.strip().split("=")
        config[key] = value

mysql_user = config["mysql_user"]
mysql_password = config["mysql_password"]
# MySQL connection
con=mysql.connect(host="localhost",password=mysql_password,user=mysql_user,database="GST")
cur=con.cursor()
#GLOBAL VARIABLES

GST_dict={"Luxury":28,"Electronics":18,"Household":12,"Food":10}
GSTIN=""
business_Name=""
Pass=""

#FUNCTIONS
def positive_number(x):
    try:
        return float(x)>0
    except ValueError:
        return False

def is_positive_integer(x):
    try:
        return int(x)>0
    except ValueError:
        return False

def  login():
    global GSTIN,business_Name,Pass
    GSTIN=(GST_inp.get()).strip()
    business_Name=(name_inp.get()).strip()
    Pass=(pass_inp.get()).strip()
        
    #PRELIMINARY CHECK
    if GSTIN =="" or business_Name=="" or Pass =="":
        messagebox.showerror("ERROR","PLEASE ENTER ALL FIELDS!")
        return


    #GSTIN CHECK
            
    if GSTIN.isalpha() or GSTIN.isdigit():
        messagebox.showerror("INVALID INPUT","GSTIN SHOULD CONTAIN BOTH LETTERS AND NUMBERS!")
        GST_inp.delete(0,ctk.END)
        return
        
    if GSTIN!="" and not GSTIN.isalnum():
        messagebox.showerror("ERROR","GSTIN CANNOT CONTAIN ANY WHITE SPACES!")
        GST_inp.delete(0,ctk.END)
        return
        
    if len(GSTIN)!=15:
        messagebox.showerror("INVALID INPUT","GSTIN SHOUD BE OF 15 CHARACTERS!")
        GST_inp.delete(0,ctk.END)
        return
    cur.execute(f"SELECT * FROM USERS WHERE GSTIN='{GSTIN}' AND BNAME='{business_Name}' AND PASSWORD='{Pass}'")
    user_exist= cur.fetchone()  
    if user_exist is None:
        messagebox.showerror("ERROR","INVALID LOGIN INFORMATION!")
        return
    
    
    
    click_login()

def DONE():
    GST_done=(GST_reg.get()).strip()
    Name_done=(Name_reg.get()).strip()
    Pass_done=(Pass_reg.get()).strip()
    
    if GST_done=="" or Name_done=="" or Pass_done=="":
        messagebox.showerror("ERROR","Please enter all fields!")
        return
    if GST_done.isalpha() or GST_done.isdigit():
        messagebox.showerror("INVALID INPUT","GSTIN SHOULD CONTAIN BOTH LETTERS AND NUMBERS!")
        GST_reg.delete(0,ctk.END)
        return
        
    if GST_done!="" and not GST_done.isalnum():
        messagebox.showerror("ERROR","GSTIN CANNOT CONTAIN ANY WHITE SPACES!")
        GST_reg.delete(0,ctk.END)
        return
        
    if len(GST_done)!=15:
        messagebox.showerror("INVALID INPUT","GSTIN SHOUD BE OF 15 CHARACTERS!")
        GST_reg.delete(0,ctk.END)
        return
    
    # CHECK DUPLICATE
    cur.execute("SELECT * FROM USERS WHERE GSTIN=%s", (GST_done,))
    if cur.fetchone():
        messagebox.showerror("ERROR", "User already exists! Please login.")
        return
    
    #INSERT INFO
    cur.execute(f"INSERT INTO USERS VALUES('{GST_done}','{Name_done}','{Pass_done}')")
    con.commit()
    messagebox.showinfo("SUCCESS","Account Created!")
    win3.destroy()
    win.deiconify()
   
def click_signup():
    global GST_reg,Name_reg,Pass_reg,win3
    win3=ctk.CTkToplevel(win)
    win3.geometry("400x200+600+300")
    win3.resizable(False,False)
    win3.title("GST Invoice Generator-Signup")
    
    #LABELS
    Title_label=ctk.CTkLabel(win3,text="Signup for the the GST Invoice Generator!",font=("Segoe UI",17,"bold"))
    Title_label.grid(column=0,row=0,padx=43.5)

    #INPUT BOXES
    GST_reg=ctk.CTkEntry(win3,placeholder_text="GSTIN",width=250)
    Name_reg=ctk.CTkEntry(win3,placeholder_text="Business Name",width=250)
    Pass_reg=ctk.CTkEntry(win3,placeholder_text="Password",show="●",width=250)
    GST_reg.grid(row=2,column=0,pady=5)
    Name_reg.grid(row=3,column=0,pady=5)
    Pass_reg.grid(row=4,column=0,pady=5)

    done_button=ctk.CTkButton(win3,text="Done",font=("Inter",16,"bold"),width=250,command=DONE)
    done_button.grid(row=5,column=0,pady=5)
    win.withdraw()
    win3.protocol("WM_DELETE_WINDOW", win.destroy)
    
def Old_invoices():
    global search_box,invoices_table
    win4=ctk.CTkToplevel(win2)
    win4.geometry("800x420+500+200")
    win4.resizable(False,False)
    win4.columnconfigure(0,weight=1)
    win4.title("View old invoices!")
    
    #SEARCH BAR 
    together_3=ctk.CTkFrame(win4,fg_color="transparent")
    together_3.grid(row=0,column=0,padx=10,pady=10,sticky='ew')
    search_box=ctk.CTkEntry(together_3,width=250,placeholder_text="INVOICE ID")
    search_box.grid(row=0,column=0,padx=5,pady=5)
    search_button=ctk.CTkButton(together_3,text="SEARCH",font=("Inter",16,"bold"),width=100,command=Search)
    search_button.grid(row=0,column=1)
    show_All=ctk.CTkButton(together_3,text="SHOW ALL",font=("Inter",16,"bold"),width=100,command=Show_all)
    show_All.grid(row=0,column=2,padx=5)
    
    #TABLE 
    invoices_table=ttk.Treeview(win4,columns=("INVOICE_ID","CUSTOMER NAME","DATE","GRAND TOTAL"),show="headings",height=10)
    invoices_table.heading("INVOICE_ID",text="INVOICE_ID")
    invoices_table.heading("CUSTOMER NAME",text="CUSTOMER NAME")
    invoices_table.heading("DATE",text="DATE OF INVOICE")
    invoices_table.heading("GRAND TOTAL",text="GRAND TOTAL")
    invoices_table.column("INVOICE_ID",anchor="center")
    invoices_table.column("CUSTOMER NAME",anchor="center")
    invoices_table.column("DATE",anchor="center")
    invoices_table.column("GRAND TOTAL",anchor="center")
    style =ttk.Style(win4)
    style.theme_use("clam")
    style.configure("Treeview", background="#2a2a2a",foreground="white",rowheight=25,fieldbackground="#2a2a2a", borderwidth=0)
    invoices_table.grid(row=1,column=0,pady=(10,0))
    
    together_4=ctk.CTkFrame(win4,fg_color="transparent")
    together_4.grid(row=2,column=0,pady=10,sticky='ew')
    regenerate_button=ctk.CTkButton(together_4,text="REGENERATE PDF",font=("Inter",16,"bold"),width=150,command=Re_generate)
    regenerate_button.grid(row=0,column=0,padx=5)
    delete_invoice=ctk.CTkButton(together_4,text="DELETE SELECTED INVOICE",font=("Inter",16,"bold"),width=150,command=Delete_invoice)
    delete_invoice.grid(row=0,column=1,padx=5)
    
    scrollbar1 = ttk.Scrollbar(win4, orient="vertical", command=invoices_table.yview)
    invoices_table.configure(yscrollcommand=scrollbar1.set)
    scrollbar1.grid(row=1, column=1, sticky="ns", pady=(10, 0))
    
    
    
    win2.withdraw()
    win4.protocol("WM_DELETE_WINDOW",lambda:[win2.deiconify(),win4.destroy()])

def Delete_invoice():
    selection= invoices_table.selection()
    if not selection:
        messagebox.showerror("Error","Please select atleast one invoice to delete")
        return
    
    if len(selection)>1:
        messagebox.showerror("Error","Please select only one invoice to delete at a time!")
        return        
    confirm=messagebox.askyesno("CONFIRM","ARE YOU SURE YOU WANT TO DELETE THIS INVOICE/S ?")
    if not confirm:
        return
    
    ID = invoices_table.item(selection[0])['values'][0]
    cur.execute(f"DELETE FROM ITEMS WHERE INVOICE_ID={ID}")
    cur.execute(f"DELETE FROM INVOICES WHERE INVOICE_ID={ID}")
    con.commit()
    
    invoices_table.delete(selection[0])
    messagebox.showinfo("SUCCESS", "Invoice deleted successfully!")
       
def Search():
    search_text=(search_box.get()).strip()

    for row in invoices_table.get_children():
        invoices_table.delete(row)
    
    if search_text=="":
        messagebox.showerror("Error","Please enter something to search")
        return
    if not search_text.isdigit():
        messagebox.showerror("Error","Please enter a valid invoice  to search")
        return
    if not is_positive_integer(search_text):
        messagebox.showerror("Error","Please enter a valid invoice  to search")
        return

    
    cur.execute(f"SELECT invoice_id,CNAME,INVOICE_DATE,GRAND_TOTAL FROM INVOICES WHERE invoice_id={search_text}")
    rows=cur.fetchall()
    
    if not rows:
        messagebox.showerror("ERROR","No invoices found!")
        return
    for row in rows:
        invoices_table.insert("","end",values=row)
    
def Show_all():
    for row in invoices_table.get_children():
        invoices_table.delete(row)
        
    cur.execute(f"SELECT invoice_id,CNAME,INVOICE_DATE,GRAND_TOTAL FROM INVOICES WHERE GSTIN='{GSTIN}'")
    rows=cur.fetchall()
    for row in rows:
        invoices_table.insert("","end",values=row)
        
def click_login():
    global product_entry,category_dropdown,cost_entry,quantity_entry,table, addr_entry,phn_entry,cadd_entry,cphn_entry,cname_entry,win2

    win2=ctk.CTkToplevel(win)

    win2.geometry("800x720+500+200")
    win2.resizable(False,False)
    win2.columnconfigure(0, weight=1)
    win2.title("GST Invoice Generator-Dashboard")
    dash_label=ctk.CTkLabel(win2,text="Dashboard",font=("Arial Black",25,"bold"))
    dash_label.grid(row=0,column=0,stick="w",padx=5,pady=(5,0))
    business_label=ctk.CTkLabel(win2,text="Business Address",font=("Arial Black",13,"bold"))
    business_label.grid(row=1,column=0,sticky="W",padx=5)
    addr_entry=ctk.CTkTextbox(win2,width=200,height=60)
    addr_entry.grid(row=2,column=0,sticky="W",padx=5)
    phone_label=ctk.CTkLabel(win2,text="Business Phone Number",font=("Arial Black",13,"bold"))
    phone_label.grid(row=3,column=0,sticky="W",padx=5)
    phn_entry=ctk.CTkEntry(win2,width=200)
    phn_entry.grid(row=4,column=0,sticky="W",padx=5)
    cust_add=ctk.CTkLabel(win2,text="Customer Address",font=("Arial Black",13,"bold"))
    cust_add.grid(row=1,column=0,sticky="e",padx=5)
    cadd_entry=ctk.CTkTextbox(win2,width=200,height=60)
    cadd_entry.grid(row=2,column=0,sticky="e",padx=5)
    cphone_label=ctk.CTkLabel(win2,text="Customer Phone Number",font=("Arial Black",13,"bold"))
    cphone_label.grid(row=3,column=0,sticky="e",padx=5)
    cphn_entry=ctk.CTkEntry(win2,width=200)
    cphn_entry.grid(row=4,column=0,sticky="e",padx=5)
    cname_label=ctk.CTkLabel(win2,text="Customer Name",font=("Arial Black",13,"bold"))
    cname_label.grid(row=5,column=0,sticky="e",padx=5)
    cname_entry=ctk.CTkEntry(win2,width=200)
    cname_entry.grid(row=6,column=0,sticky="e",padx=5)

    #item fields
    together=ctk.CTkFrame(win2,fg_color="transparent")
    together.grid(row=7,column=0,sticky="ew", padx=5, pady=(40, 0))
    product_label=ctk.CTkLabel(together,text="Product",font=("Arial Black",13,"bold"))
    product_label.grid(row=0,column=0,sticky="w",padx=5)
    product_entry=ctk.CTkEntry(together,width=150)
    product_entry.grid(row=1,column=0,sticky="w",padx=5)
    category_label=ctk.CTkLabel(together,text="Category",font=("Arial Black",13,"bold"))
    category_label.grid(row=0,column=1,sticky="w",padx=15)
    category_dropdown=ctk.CTkOptionMenu(together,width=150,values=["Luxury","Food","Electronics","Household"])
    category_dropdown.grid(row=1,column=1,sticky="w",padx=15)
    cost_label=ctk.CTkLabel(together,text="Cost",font=("Arial Black",13,"bold"))
    cost_label.grid(row=0,column=2,sticky="w",padx=15)
    cost_entry=ctk.CTkEntry(together,width=150)
    cost_entry.grid(row=1,column=2,sticky="w",padx=15)
    quantity_label=ctk.CTkLabel(together,text="Quantity",font=("Arial Black",13,"bold"))
    quantity_label.grid(row=0,column=3,sticky="w",padx=15)
    quantity_entry=ctk.CTkEntry(together,width=150)
    quantity_entry.grid(row=1,column=3,sticky="w",padx=15)


    #treeview table
    table=ttk.Treeview(win2,columns=("Product","Cost","GST","Quantity"),show="headings",height=10)
    table.heading("Product",text="Product")
    table.heading("Cost",text="Cost")
    table.heading("GST",text="GST")
    table.heading("Quantity",text="Quantity")
    table.column("Product",anchor="center")
    table.column("Cost",anchor="center")
    table.column("GST",anchor="center")
    table.column("Quantity",anchor="center")
    style =ttk.Style(win2)
    style.theme_use("clam")
    style.configure("Treeview", background="#2a2a2a",foreground="white",rowheight=25,fieldbackground="#2a2a2a", borderwidth=0)
    table.grid(row=8,column=0,pady=(15,0))
    
    scrollbar = ttk.Scrollbar(win2, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)

    scrollbar.grid(row=8, column=1, sticky="ns", pady=(15, 0))

    #bottom buttons
    together_2=ctk.CTkFrame(win2,fg_color="transparent")
    together_2.grid(row=9,column=0,sticky="ew", padx=5, pady=(40, 0))
    add_button=ctk.CTkButton(together_2,text="ADD",font=("Inter",16,"bold"),width=100,command=ADD_button)
    add_button.grid(row=0,column=0,padx=5)
    submit_button=ctk.CTkButton(together_2,text="SUBMIT",font=("Inter",16,"bold"),width=100,command=SUBMIT_button)
    submit_button.grid(row=0,column=1,padx=5)
    remove_button=ctk.CTkButton(together_2,text="REMOVE SELECTED",font=("Inter",16,"bold"),width=100,command=REMOVE_button)
    remove_button.grid(row=0,column=2,padx=5)
    view_old_button=ctk.CTkButton(together_2,text="VIEW OLD INVOICES",font=("Inter",16,"bold"),width=150,command=Old_invoices)
    view_old_button.grid(row=0,column=3,padx=5)
    
    

    win.withdraw()
    win2.protocol("WM_DELETE_WINDOW", win.destroy)
    
def Re_generate():
    selected = invoices_table.selection()
    if not selected:
        messagebox.showerror("ERROR", "Please select an invoice to regenerate!")
        return

    row_values = invoices_table.item(selected[0])['values']
    sel_invoice_id = row_values[0]

    cur.execute(f"SELECT GSTIN, BADDR, BPHN, CNAME, CPHN, CADDR, INVOICE_DATE, SUBTOTAL, GRAND_TOTAL FROM INVOICES WHERE INVOICE_ID={sel_invoice_id}")
    inv = cur.fetchone()
    if not inv:
        messagebox.showerror("ERROR", "Invoice data not found!")
        return

    sel_GSTIN, sel_Baddr, sel_Bphn, sel_Cname, sel_Cphn, sel_Caddr, sel_date, sel_Sub_Total, sel_Grand_Total = inv

    cur.execute(f"SELECT BNAME FROM USERS WHERE GSTIN='{sel_GSTIN}'")
    bname_row = cur.fetchone()
    sel_Bname = bname_row[0] if bname_row else "Unknown"

    # CORRECTED COLUMN NAME: ITEM_NAME
    cur.execute(f"SELECT ITEM_NAME, COST, GST, QUANTITY, AMOUNT, AMOUNT_GST FROM ITEMS WHERE INVOICE_ID={sel_invoice_id}")
    items = cur.fetchall()
    if not items:
        messagebox.showerror("ERROR", "No items found for this invoice!")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")],
        initialfile=f"Invoice_{sel_invoice_id}"
    )
    if not path:
        return

    invoice_canvas = canvas.Canvas(path, pagesize=A4)
    W, H = A4
    y = H - 50

    invoice_canvas.setFont("Helvetica-Bold", 14)
    invoice_canvas.drawString(50, y, "GST TAX INVOICE")
    y-=30

    invoice_canvas.setFont("Helvetica-Bold", 11)
    invoice_canvas.drawString(50, y, f"Business Name: {sel_Bname}")
    y-=18
    invoice_canvas.drawString(50, y, f"Business Address: {sel_Baddr}")
    y-=18
    invoice_canvas.drawString(50, y, f"Business Phone: {sel_Bphn}")
    y -= 18
    invoice_canvas.drawString(50, y, f"GSTIN: {sel_GSTIN}")
    y-=30

    invoice_canvas.drawString(50, y, f"Invoice No: {sel_invoice_id}")
    y-=18
    invoice_canvas.drawString(50, y, f"Date: {sel_date.strftime('%d-%m-%Y') if hasattr(sel_date, 'strftime') else sel_date}")
    y-=30

    invoice_canvas.drawString(50, y, f"Customer Name: {sel_Cname}")
    y-=18
    invoice_canvas.drawString(50, y, f"Customer Phone: {sel_Cphn}")
    y-=18
    invoice_canvas.drawString(50, y, f"Customer Address: {sel_Caddr}")
    y-=30

    invoice_canvas.setStrokeColor(colors.black)
    invoice_canvas.setLineWidth(0.5)
    invoice_canvas.line(50, y, W - 50, y)
    y -= 15

    data = [["Item", "Qty", "Rate", "GST", "Amount"]]
    for item in items:
        item_name, cost, gst, qty, amount, amount_gst = item
        data.append([item_name, str(qty), f"{float(cost):.2f}", f"{gst}%", f"{float(amount_gst):.2f}"])

    data.append(["", "", "", "Subtotal",    f"{float(sel_Sub_Total):.2f}"])
    data.append(["", "", "", "Grand Total", f"{float(sel_Grand_Total):.2f}"])

    t = Table(data, colWidths=[150, 60, 60, 60, 80])
    t.wrapOn(invoice_canvas, W, H)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0),  (-1, 0),  colors.HexColor("#444444")),
        ("TEXTCOLOR",     (0, 0),  (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0),  (-1, 0),  "Helvetica-Bold"),
        ("FONTNAME",      (0, 1),  (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0),  (-1, -1), 10),
        ("ALIGN",         (0, 0),  (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS",(0, 1),  (-1, -2), [colors.HexColor("#f5f5f5"), colors.white]),
        ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#dddddd")),
        ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID",          (0, 0),  (-1, -1), 0.5, colors.black),
        ("TOPPADDING",    (0, 0),  (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0),  (-1, -1), 6),
    ]))
    t.drawOn(invoice_canvas, 50, y - (len(data) * 20))
    y = y - (len(data) * 20) - 20

    invoice_canvas.line(50, y, W - 50, y)
    y -= 20

    invoice_canvas.setFont("Helvetica", 11)
    invoice_canvas.drawString(50, y, f"Subtotal:      {float(sel_Sub_Total):.2f}")
    y -= 18
    invoice_canvas.setFont("Helvetica-Bold", 11)
    invoice_canvas.drawString(50, y, f"Grand Total:   {float(sel_Grand_Total):.2f}")

    invoice_canvas.save()
    messagebox.showinfo("Done", "PDF Regenerated Successfully!")
    
def ADD_button():
    global product,category,cost,quantity
    product=(product_entry.get()).strip()
    category=category_dropdown.get()
    cost=(cost_entry.get()).strip()
    quantity=(quantity_entry.get()).strip()
    
    #PRELIMINARY CHECK
    if product=="" or cost=="" or quantity=="":
        messagebox.showerror("ERROR","Please fill all fields!")

        return
    
    #FIELD SPECIFIC CHECK
    
    for i in cost:
        if not i.isdigit():
            messagebox.showerror("ERROR","please enter value without white spaces and anything other than numbers")
            return

        
    if not positive_number(cost):
        messagebox.showerror("ERROR","Please enter an integer value greater than 0 for cost!")
        cost_entry.delete(0,ctk.END)
        return
    


        
    
    if not is_positive_integer(quantity):
        messagebox.showerror("ERROR","Please enter integers greater than 0 for quantity!")
        quantity_entry.delete(0,ctk.END)
        return
    
    table.insert("","end",values=(product,cost,str(GST_dict[category])+"%",quantity))
    product_entry.delete(0,ctk.END)
    cost_entry.delete(0,ctk.END)
    quantity_entry.delete(0,ctk.END)

def REMOVE_button():
    selected_items=table.selection()
    if not selected_items:
        messagebox.showerror("ERROR","Please select something to remove!")
        return  

    table.delete(selected_items)
    
def SUBMIT_button():
    global Baddr,Bphn,Caddr,Cphn,Cname,invoice_id,Grand_Total,Sub_Total
    Baddr=(addr_entry.get("1.0","end")).strip()

    Bphn=(phn_entry.get()).strip()
    Caddr=(cadd_entry.get("1.0","end")).strip()
    Cphn=(cphn_entry.get()).strip()
    Cname=(cname_entry.get()).strip()
    
    Baddr = Baddr.replace("\n", " ")
    Caddr = Caddr.replace("\n", " ")
    #PRELIMINARY CHECK
    if Baddr=="" or Bphn=="" or Caddr=="" or Cphn=="" or Cname=="":
        messagebox.showerror("ERROR","Please fill all fields!")
        return
    if not is_positive_integer(Bphn):
        messagebox.showerror("ERROR","Please enter valid b usiness phone number")
        return
    if not is_positive_integer(Cphn):
        messagebox.showerror("ERROR","Please enter valid customer phone number")
        return
    if len(Cphn)!=10:
        messagebox.showerror("ERROR","Please enter valid customer phone number")
        return
    
    if len(Bphn)!=10:
        messagebox.showerror("ERROR","Please enter valid business phone number")
        return    
    #READING RECORDS FROM THE TABLE 
    item_ids=table.get_children()
    if len(item_ids)==0:
        messagebox.showerror("ERROR","Please add atleast one item")
        return
    
    
    #ADDITION TO INVOICES TABLE (WITHOUT SUBTOTAL AND GRAND TOTAL {ADDED LATER})
    today = date.today().strftime("%Y-%m-%d")
    cur.execute(f"INSERT INTO INVOICES(GSTIN,BADDR,BPHN,INVOICE_DATE,CNAME,CPHN,CADDR) VALUES('{GSTIN}','{Baddr}','{Bphn}','{today}','{Cname}','{Cphn}','{Caddr}')")
    con.commit()
    #ADDITION TO ITEMS TABLE
    invoice_id=cur.lastrowid
    for i in item_ids:
        l=table.item(i)['values']
        p=l[0]
        c=float(l[1])
        g=int(l[2].replace("%",""))
        q=int(l[3])
        cur.execute(f"INSERT INTO ITEMS VALUES({invoice_id},'{p}','{c}',{g},'{q}','{c*q}','{(c*q)+((c*q)*(g/100))}')")
        con.commit()
    
    #INSERT SUBTOTAL AND GRAND TOTAL
    cur.execute(f"SELECT SUM(AMOUNT) FROM ITEMS WHERE INVOICE_ID={invoice_id}")
    Sub_Total=cur.fetchone()[0]
    cur.execute(f"UPDATE INVOICES SET SUBTOTAL={Sub_Total} WHERE INVOICE_ID= {invoice_id} ")
    con.commit()
    cur.execute(f"SELECT SUM(AMOUNT_GST) FROM ITEMS WHERE INVOICE_ID={invoice_id}")
    Grand_Total=cur.fetchone()[0]
    cur.execute(f"UPDATE INVOICES SET GRAND_TOTAL={Grand_Total} WHERE INVOICE_ID={invoice_id}")
    con.commit()
    messagebox.showinfo("Generating","Generating your PDF!")
    Generate_pdf()
   
def Generate_pdf():
    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF","*.pdf")])
    if not path:
        return
    
    invoice = canvas.Canvas(path, pagesize=A4)
    W, H = A4
    y = H - 50  # starting y position, we'll move down as we draw

    # TITLE
    invoice.setFont("Helvetica-Bold", 14)
    invoice.drawString(50, y, "GST TAX INVOICE")
    y -= 30

    # BUSINESS DETAILS
    invoice.setFont("Helvetica-Bold", 11)
    invoice.drawString(50, y, f"Business Name: {business_Name}")
    y -= 18
    invoice.drawString(50, y, f"Business Address: {Baddr}")
    y -= 18
    invoice.drawString(50, y, f"Business Phone: {Bphn}")
    y -= 18
    invoice.drawString(50, y, f"GSTIN: {GSTIN}")
    y -= 30

    # INVOICE DETAILS
    invoice.drawString(50, y, f"Invoice No: {invoice_id}")
    y -= 18
    invoice.drawString(50, y, f"Date: {date.today().strftime('%d-%m-%Y')}")
    y -=30

    # CUSTOMER DETAILS
    invoice.drawString(50, y, f"Customer Name: {Cname}")
    y -=18
    invoice.drawString(50, y, f"Customer Phone: {Cphn}")
    y-= 18
    invoice.drawString(50, y, f"Customer Address: {Caddr}")
    y-= 30

    # DIVIDER
    invoice.setStrokeColor(colors.black)
    invoice.setLineWidth(0.5)
    invoice.line(50, y, W-50, y)
    y -=15

    # ITEMS TABLE
    data = [["Item", "Qty", "Rate", "GST", "Amount"]]
    for row in table.get_children():
        vals = table.item(row)["values"]
        Product, Cost, Gst, Qty = vals
        total = float(Cost) * int(Qty) * (1 + int(Gst.replace("%","")) / 100)
        data.append([Product, Qty, Cost, Gst, f"{total:.2f}"])
    
    data.append(["", "", "", "Subtotal", f"{Sub_Total:.2f}"])
    data.append(["", "", "", "Grand Total", f"{Grand_Total:.2f}"])

    t = Table(data, colWidths=[150, 60, 60, 60, 80])
    t.wrapOn(invoice, W, H)
    t.setStyle(TableStyle([
    # HEADER ROW
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#444444")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    
    # BODY ROWS
    ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 10),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("ROWBACKGROUNDS", (0,1), (-1,-2), [colors.HexColor("#f5f5f5"), colors.white]),
    
    # GRAND TOTAL ROW
    ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#dddddd")),
    ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
    
    # GRID
    ("GRID", (0,0), (-1,-1), 0.5, colors.black),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    t.drawOn(invoice, 50, y - (len(data) * 20))
    y = y - (len(data) * 20) - 20

    # DIVIDER
    invoice.line(50, y, W-50, y)
    y -= 20

    # SUBTOTAL AND GRAND TOTAL
    invoice.setFont("Helvetica", 11)
    invoice.drawString(50, y, f"Subtotal:      {Sub_Total:.2f}")
    y -= 18
    invoice.setFont("Helvetica-Bold", 11)
    invoice.drawString(50, y, f"Grand Total:   {Grand_Total:.2f}")

    invoice.save()
    messagebox.showinfo("Done", "PDF Generated!")
    

#LOGIN PAGE

#WINDOW INITIALISATION
win=ctk.CTk()
win.geometry("400x400+600+300")
win.resizable(False,False)
win.title("GST invoice generator")

#LABELS
Title_label=ctk.CTkLabel(win,text="Welcome to the GST Invoice Generator!",font=("Segoe UI",17,"bold"))
Title_label.grid(column=0,row=0,padx=43.5)
login_label=ctk.CTkLabel(win,text="Login",font=("aerial",15,"bold"))
login_label.grid(row=1,column=0,pady=30)
or_label=ctk.CTkLabel(win,text="OR",font=("aerial,",10,"bold"))
or_label.grid(row=6,column=0)

#INPUT BOXES
GST_inp=ctk.CTkEntry(win,placeholder_text="GSTIN",width=250)
name_inp=ctk.CTkEntry(win,placeholder_text="Business Name",width=250)
pass_inp=ctk.CTkEntry(win,placeholder_text="Password",show="●",width=250)
GST_inp.grid(row=2,column=0,pady=3)
name_inp.grid(row=3,column=0,pady=3)
pass_inp.grid(row=4,column=0,pady=3)

#BUTTONS
login_button=ctk.CTkButton(win,text="Login",font=("Inter",16,"bold"),width=250,command=login)
login_button.grid(row=5,column=0,pady=(20,0))
signup_button=ctk.CTkButton(win,text="SignUp",font=("Inter",16,"bold"),width=250,fg_color="Black",text_color="Blue",border_color="#133aba",border_width=2,command=click_signup)
signup_button.grid(row=7,column=0,)

win.mainloop()