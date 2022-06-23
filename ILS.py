# -*- coding: cp1252 -*-

#Import BUILD-IN functions
from tkinter import *
import tkinter.ttk as ttk
from time import strftime, sleep

#Import LOCAL functions
from db.db_connect import SQL_Connect, Get_Employees, Update_SQL_Data_Prepared, Get_Devices, Get_Assingment, Serial_Connect, Get_SQL_Data
from fnct.getpath import Get_Local_Path
from db.db_txt import Connection_Dict, Serial_Dict
import datetime
from datetime import datetime
from tkcalendar import DateEntry

def File_Permission_Update():
    db_params_file = Get_Local_Path() + "\db\db_params.txt"
    ser_params_file = Get_Local_Path() + "\db\ser_params.txt"
    import os, getpass
    usrname = getpass.getuser()
    try:
        os.system('CACLS "' + db_params_file + '" /e /p ' + usrname + ':f')
        os.system('CACLS "' + ser_params_file + '" /e /p ' + usrname + ':f')
    except Exception as e:
        print(e)
File_Permission_Update()

def Refresh(self):
    self.destroy()
    self.__init__()

def Clear(frame_name):
    for widgets in frame_name.winfo_children():
      widgets.destroy()

def Update_Label(label, textvar, inputtext, color):
    style = ttk.Style()
    style.configure("Red.Label", foreground=color)
    label.configure(style = "Red.Label")
    textvar.set(inputtext)
    label.config(text=textvar.get())

def Send_Serial(char):
    ser.flush()
    sleep(0.1)
    char = char + "*"
    ser.write(char.encode())

connection_params = Connection_Dict()
serial_params = Serial_Dict()
current_directory = Get_Local_Path()
#########################################
#TKINTER WINDOWS CONFIGURATIONS
#Main window options
main_window = Tk()
main_window.title("- Narzedziownia")
main_window.geometry("1200x800")
main_window.iconbitmap(current_directory + "\img\ils.ico")

left_buttons_panel = ttk.Label(main_window, anchor=W)
left_buttons_panel.pack(side=LEFT, fill=Y)
right_buttons_panel = ttk.Label(main_window, anchor=E)
right_buttons_panel.pack(side=RIGHT, fill=Y)
top_buttons_panel = ttk.Label(main_window, anchor=N)
top_buttons_panel.pack(side=TOP, fill=X)



scrollframe = Frame(main_window)
scrollframe.pack(side=TOP, fill=BOTH, expand=True)

vscrollbar = Scrollbar(scrollframe, orient='vertical')

middle_screen = Canvas(scrollframe, yscrollcommand=vscrollbar.set)

vscrollbar.config(command=middle_screen.yview)
vscrollbar.pack(side=RIGHT, fill=Y)

middle_screen_panel = Frame(middle_screen)

middle_screen.pack(side=TOP, fill=BOTH, expand=True)

middle_screen.create_window(0,0,window=middle_screen_panel, anchor='n', width=1000)

main_window.update()
middle_screen.update()
middle_screen_panel.update()
middle_screen.config(scrollregion=middle_screen.bbox("all"))



try:
    ser = Serial_Connect(serial_params['com'], serial_params['baud'], serial_params['datasize'], serial_params['parity'])
except Exception as e:
    print(e)
    #Update_Label(main_communicate_label, main_communicate, "Nie mozna otworzyc portu - " + str(e), "red")

ser_check = 0
waiting_status = 'emp'
waiting_time = 0
emp_name = ""
def Read_Serial():
    try:
        try:
            conn = SQL_Connect(connection_params['host'], connection_params['password'], connection_params['ip'], connection_params['database'], connection_params['port'])
        except Exception as e:
            Update_Label(main_communicate_label, main_communicate, "Blad polaczenia z baza danych.\n" + str(e), "red")
        global emp_name
        global waiting_time
        global waiting_status
        global ser_check
        if waiting_time == 5000:
            waiting_time = 0
            Send_Serial("n0")
            Send_Serial("b0")
            Send_Serial("r0")
            Update_Label(main_communicate_label, main_communicate, "Wszystko OK, czekam na skan.", "black")
            waiting_status = 'emp'

        if ser_check == 0:
            sleep(2)
            Send_Serial("g1")
            ser_check += 1

        if ser.inWaiting() > 3 and waiting_status == 'emp':
            waiting_time = 0
            card_id = str(ser.readline())[2:-5]
            #print(card_id)
            if card_id == "POWER by PDAserwis":
                Update_Label(main_communicate_label, main_communicate, "Wszystko OK. Czekam na skan.", "black")
            else:
                employee = Get_SQL_Data("employees", "*", "card_id", card_id)
                if employee != []:
                    emp_name = employee[0][1] + " " + employee[0][2]
                    global emp_id
                    emp_id = employee[0][0]
                    #print(emp_id)
                    Send_Serial("n1")
                    ser.flushInput()
                    ser.flushOutput()
                    #print(ser.inWaiting())
                    Update_Label(main_communicate_label, main_communicate, "Czekam na przypisanie urzadzenia do: " + emp_name, "black")
                    waiting_status = 'dev'
                    employee = []
                ##NA TYM ELSIE SKONCZYLEM
                else:
                    dev_id = str(ser.readline())[2:-5]
                    device = Get_SQL_Data("devices", "*", "rfid_id", dev_id)
                    
                    if device != []:
                        dev_type = device[0][1]
                        dev_id = device[0][0]
                        device_check = Get_SQL_Data("assingment", "*", "device", str(dev_id) + "' AND active = '1")
                        if device_check == []:
                            Update_Label(main_communicate_label, main_communicate, "Urzadzenie " + dev_type + " nie jest do nikogo przypisane", "black")
                            Send_Serial("r1")
                            sleep(1)
                            Send_Serial("r0")
                        else:
                            print(device_check)
                            actual_time = datetime.now()
                            actual_time = actual_time.strftime("%Y-%m-%d %H:%M:%S")
                            prepared_query_2 = "UPDATE assingment SET active = 0 , date_deposit = '" + actual_time + "' WHERE device = " + str(dev_id) + " AND active = 1"
                            Update_SQL_Data_Prepared(prepared_query_2)
                            Update_Label(main_communicate_label, main_communicate, "Odpialem urzadzenie " + dev_type, "black")
                            Send_Serial("b1")
                            sleep(1)
                            Send_Serial("b0")
                            device = []
                    else:
                        Update_Label(main_communicate_label, main_communicate, "Nie znaleziono karty - " + card_id + ". Zeskanuj karte pracownika", "black")
                        Send_Serial("r1")
                        sleep(1)
                        waiting_time = 5000
        elif ser.inWaiting() > 3 and waiting_status == 'dev':
            if emp_name != "":
                waiting_time = 0
                dev_id = str(ser.readline())[2:-5]
                #print(dev_id)
                device = Get_SQL_Data("devices", "*", "rfid_id", dev_id)
                if device != []:
                    dev_status = Get_SQL_Data("assingment", "*", "active", '1')
                    dev_type = device[0][1]
                    dev_id = device[0][0]
                    if dev_status != []:
                        actual_assingment = Get_SQL_Data("employees", "*", "id", str(dev_status[0][2]))
                        Update_Label(main_communicate_label, main_communicate, "Urzadzenie " + dev_type + "jest juz przypisane do: " + actual_assingment[0][1] + " " + actual_assingment[0][2], "red")
                        Send_Serial("r1")
                        sleep(1)
                        Send_Serial("r0")
                    else:
                        Update_Label(main_communicate_label, main_communicate, "Przypisano urzadzenie " + dev_type + " do: " + emp_name, "black")
                        actual_time = datetime.now()
                        actual_time = actual_time.strftime("%Y-%m-%d %H:%M:%S")
                        #print(actual_time)
                        prepared_query = "INSERT INTO assingment (device, employee, date_withdraw, active) VALUES ('" + str(dev_id) + "', '" + str(emp_id) + "', '" + actual_time + "', 1)"
                        #print(prepared_query)
                        Update_SQL_Data_Prepared(prepared_query)
                        Send_Serial("b1")
            else:
                Update_Label(main_communicate_label, main_communicate, "Zeskanuj najpierw karte pracownika", "black")
                waiting_time = 0

        if waiting_status == 'dev':
            waiting_time += 200
        ser.flushInput()
        ser.flushOutput()
        lbl.after(200, Read_Serial)
        print(waiting_status)
    except Exception as e:
        print(e)
        Update_Label(main_communicate_label, main_communicate, "Blad przy probie nawiazania polaczenia z czytnikiem RFID - " + str(e), "red")


#Middle screen tables
def Create_Table_Devices(sql_result):
    conn = SQL_Connect(connection_params['host'], connection_params['password'], connection_params['ip'], connection_params['database'], connection_params['port'])
    def Edit_Device(device_id):
        def Update_Device(device_id, device_name, device_rfidid, frame):
            sql_query = "UPDATE devices SET type = '" + device_name + "', rfid_id = '" + device_rfidid + "' WHERE id = " + str(device_id)
            Update_SQL_Data_Prepared(sql_query)
            frame.destroy()
            Create_Table_Devices(Get_Devices())
        newWindow = Toplevel()
        newWindow.title("Edytuj urzadzenie")
        newWindow.geometry("250x100")
        newWindow.iconbitmap(current_directory + "\img\ils.ico")
        sql_query = "SELECT type, rfid_id FROM devices WHERE id =  " + str(device_id)
        get_sql = conn.cursor()
        get_sql.execute(sql_query)
        output = get_sql.fetchall()
        
        s_name=StringVar()
        s_rfidid=StringVar()
        device_name = StringVar()
        device_name.set(output[0][0])
        device_rfidid = StringVar()
        device_rfidid.set(output[0][1])
        Label(newWindow, text="Nazwa:").grid(row=0, column=0, sticky='ew')
        fname = Entry(newWindow, textvariable=s_name)
        fname.grid(row=0, column=1)
        fname.insert(END, device_name.get())
        Label(newWindow, text="ID Naklejki").grid(row=1, column=0)
        lname = Entry(newWindow, textvariable=s_rfidid)
        lname.grid(row=1, column=1)
        lname.insert(END, device_rfidid.get())

        act_btn = ttk.Button(newWindow, text = "Aktualizuj", command=lambda: Update_Device(device_id, s_name.get(), s_rfidid.get(), newWindow))
        act_btn.grid(row=3, column=1, columnspan=1, sticky='ew')
    def Delete_Device(device_id, name, rfidid):
        def Deactivate_Device(dev_id):
            sql_query = "UPDATE devices SET active = 0 WHERE id = " + str(dev_id)
            Update_SQL_Data_Prepared(sql_query)
        are_you_sure = Toplevel()
        are_you_sure.title("Potwierdz wybor")
        are_you_sure.geometry("280x100")
        are_you_sure.iconbitmap(current_directory + "\img\ils.ico")
        ttk.Label(are_you_sure, text="Czy na pewno chcesz usunac:\n" + name + "?").pack(side = TOP, expand = True, fill = BOTH)
        Button(are_you_sure, text="Tak", width=10, height=1, bg="orange",command=lambda dev_id = device_id: [Deactivate_Device(str(dev_id)),Create_Table_Devices(Get_Devices()), are_you_sure.destroy(), middle_screen_panel.update()]).pack(side = TOP, expand = True, fill = BOTH)
        Button(are_you_sure, text="Nie", width=10, height=1,command=are_you_sure.destroy).pack(side = TOP, expand = True, fill = BOTH)
    def Add_Device():
        def Add_Device_Btn(name, rfidid, frame, message):
            if name != "" and name != None and rfidid != "" and rfidid != None:
                sql_query = "INSERT INTO devices (type, rfid_id, active) VALUES ('" + name + "', '" + rfidid + "', 1);"
                #print(sql_query)
                Update_SQL_Data_Prepared(sql_query)
                frame.destroy()
                Create_Table_Devices(Get_Devices())
            else:
                message.set("Uzupelnij wszystkie pola!")

        newWindow = Toplevel()
        newWindow.title("Dodaj urzadzenie")
        newWindow.geometry("250x150")
        newWindow.iconbitmap(current_directory + "\img\ils.ico")

        s_name=StringVar()
        s_rfidid=StringVar()
        global message
        message=StringVar()

        Label(newWindow, text="Nazwa:").grid(row=0, column=0, sticky='ew')
        fname = Entry(newWindow, textvariable=s_name)
        fname.grid(row=0, column=1)
        Label(newWindow, text="ID Naklejki:").grid(row=1, column=0)
        lname = Entry(newWindow, textvariable=s_rfidid)
        lname.grid(row=1, column=1)


        act_btn = ttk.Button(newWindow, text = "Dodaj", command=lambda: Add_Device_Btn(s_name.get(), s_rfidid.get(), newWindow, message))
        act_btn.grid(row=3, column=1, columnspan=1, sticky='ew')
        Label(newWindow, textvariable=message).grid(row=4, column=1, columnspan=1, sticky='ew')
    Clear(middle_screen_panel)
    Clear(top_buttons_panel)
    add_emp_btn = ttk.Button(top_buttons_panel, text="Dodaj\nurzadzenie", command=lambda: Add_Device()).pack(side=TOP, anchor=N, fill=Y)
    #scrollbar = ttk.Scrollbar(right_buttons_panel, orient='vertical', command=middle_screen_panel.yview).pack(side=LEFT, fill=Y)
    i = 1
    dict_firma = {}
    dict_firma["frame0"] = Frame(middle_screen_panel, highlightbackground="black", highlightthickness=0.5)
    dict_firma["frame0"].pack(anchor=N, fill=X)
    e_lp = ttk.Entry(dict_firma["frame0"], width=5)
    e_lp.pack(side=LEFT)
    e_lp.insert(END, "LP")
    e_lp.config(state='disabled')
    e_id = ttk.Entry(dict_firma["frame0"], width=5)
    e_id.pack(side=LEFT)
    e_id.insert(END, "ID")
    e_id.config(state='disabled')
    e_fn = ttk.Entry(dict_firma["frame0"])
    e_fn.pack(side=LEFT)
    e_fn.insert(END, "Nazwa")
    e_fn.config(state='disabled')
    e_ln = ttk.Entry(dict_firma["frame0"])
    e_ln.pack(side=LEFT)
    e_ln.insert(END, "ID Naklejki")
    e_ln.config(state='disabled')
    for event in sql_result:
        key = str("frame" + str(i))
        dict_firma[key] = Frame(middle_screen_panel, highlightbackground="black", highlightthickness=0.5)
        dict_firma[key].pack(anchor=N, fill=X)
        e = ttk.Entry(dict_firma["frame" + str(i)], width=5)
        e.pack(side=LEFT)
        e.insert(END, str(i))
        e.config(state='disabled')
        for j in range(len(event)):
            if j == 0:
                key = "device_id" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)], width=5)
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 1:
                key = "device_name" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 2:
                key = "device_rfidid" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
                e_btn = ttk.Button(dict_firma["frame" + str(i)], text = "Edytuj", command=lambda device_id = dict_firma["device_id" + str(i)].get(): Edit_Device(device_id))
                rm_btn = ttk.Button(dict_firma["frame" + str(i)], text = "Usun urzadzenie", command=lambda device_id = dict_firma["device_id" + str(i)].get(), name = dict_firma["device_name" + str(i)].get(), rfidid = dict_firma["device_rfidid" + str(i)].get(): Delete_Device(device_id, name, rfidid))
                e_btn.pack(side=LEFT)
                rm_btn.pack(side=LEFT)
                
        i+=1
    main_window.update()
    middle_screen.config(scrollregion=middle_screen.bbox("all"))
def Create_Table_Employees(sql_result):
    conn = SQL_Connect(connection_params['host'], connection_params['password'], connection_params['ip'], connection_params['database'], connection_params['port'])
    def Edit_Employee(employee_id):
        def Update_Employee(employee_id, employee_fname, employee_lname, employee_cardid, frame):
            sql_query = "UPDATE employees SET fname = '" + employee_fname + "', lname = '" + employee_lname + "', card_id = '" + employee_cardid + "' WHERE id = " + str(employee_id)
            Update_SQL_Data_Prepared(sql_query)
            frame.destroy()
            Create_Table_Employees(Get_Employees())
        newWindow = Toplevel()
        newWindow.title("Edytuj pracownika")
        newWindow.geometry("250x100")
        newWindow.iconbitmap(current_directory + "\img\ils.ico")
        #print(employee_id)
        sql_query = "SELECT fname, lname, card_id FROM employees WHERE id =  " + str(employee_id)
        get_sql = conn.cursor()
        get_sql.execute(sql_query)
        output = get_sql.fetchall()
        
        s_fname=StringVar()
        s_lname=StringVar()
        s_cardid=StringVar()
        employee_fname = StringVar()
        employee_fname.set(output[0][0])
        employee_lname = StringVar()
        employee_lname.set(output[0][1])
        employee_cardid = StringVar()
        employee_cardid.set(output[0][2])
        #print(employee_fname.get())
        Label(newWindow, text="Imie:").grid(row=0, column=0, sticky='ew')
        fname = Entry(newWindow, textvariable=s_fname)
        fname.grid(row=0, column=1)
        fname.insert(END, employee_fname.get())
        Label(newWindow, text="Nazwisko:").grid(row=1, column=0)
        lname = Entry(newWindow, textvariable=s_lname)
        lname.grid(row=1, column=1)
        lname.insert(END, employee_lname.get())
        Label(newWindow, text="ID karty").grid(row=2, column=0)
        cardid = Entry(newWindow, textvariable=s_cardid)
        cardid.grid(row=2, column=1)
        cardid.insert(END, employee_cardid.get())

        act_btn = ttk.Button(newWindow, text = "Aktualizuj", command=lambda: Update_Employee(employee_id, s_fname.get(), s_lname.get(), s_cardid.get(), newWindow))
        act_btn.grid(row=3, column=1, columnspan=1, sticky='ew')
    def Delete_Employee(employee_id, fname, lname):
        def Deactivate_Employee(emp_id):
            sql_query = "UPDATE employees SET active = 0 WHERE id = " + str(emp_id)
            Update_SQL_Data_Prepared(sql_query)
        are_you_sure = Toplevel()
        are_you_sure.title("Potwierdz wybor")
        are_you_sure.geometry("280x100")
        are_you_sure.iconbitmap(current_directory + "\img\ils.ico")
        ttk.Label(are_you_sure, text="Czy na pewno chcesz usunac:\n" + fname + " " + lname + "?").pack(side = TOP, expand = True, fill = BOTH)
        Button(are_you_sure, text="Tak", width=10, height=1, bg="orange",command=lambda emp_id = employee_id: [Deactivate_Employee(str(emp_id)),Create_Table_Employees(Get_Employees()), are_you_sure.destroy(), middle_screen_panel.update()]).pack(side = TOP, expand = True, fill = BOTH)
        Button(are_you_sure, text="Nie", width=10, height=1,command=are_you_sure.destroy).pack(side = TOP, expand = True, fill = BOTH)
    def Add_Employee():
        def Add_Employee_Btn(fname, lname, cardid, frame, message):
            if fname != "" and fname != None and lname != "" and lname != None and cardid != "" and cardid != None:
                sql_query = "INSERT INTO employees (fname, lname, card_id, active) VALUES ('" + fname + "', '" + lname + "', '" + cardid + "', 1);"
                #print(sql_query)
                Update_SQL_Data_Prepared(sql_query)
                frame.destroy()
                Create_Table_Employees(Get_Employees())
            else:
                message.set("Uzupelnij wszystkie pola!")

        newWindow = Toplevel()
        newWindow.title("Dodaj pracownika")
        newWindow.geometry("250x150")
        newWindow.iconbitmap(current_directory + "\img\ils.ico")

        s_fname=StringVar()
        s_lname=StringVar()
        s_cardid=StringVar()
        global message
        message=StringVar()

        Label(newWindow, text="Imie:").grid(row=0, column=0, sticky='ew')
        fname = Entry(newWindow, textvariable=s_fname)
        fname.grid(row=0, column=1)
        Label(newWindow, text="Nazwisko:").grid(row=1, column=0)
        lname = Entry(newWindow, textvariable=s_lname)
        lname.grid(row=1, column=1)
        Label(newWindow, text="ID karty").grid(row=2, column=0)
        cardid = Entry(newWindow, textvariable=s_cardid)
        cardid.grid(row=2, column=1)

        act_btn = ttk.Button(newWindow, text = "Dodaj", command=lambda: Add_Employee_Btn(s_fname.get(), s_lname.get(), s_cardid.get(), newWindow, message))
        act_btn.grid(row=3, column=1, columnspan=1, sticky='ew')
        Label(newWindow, textvariable=message).grid(row=4, column=1, columnspan=1, sticky='ew')

    Clear(middle_screen_panel)
    Clear(top_buttons_panel)
    add_emp_btn = ttk.Button(top_buttons_panel, text="Dodaj\npracownika", command=lambda: Add_Employee()).pack(side=TOP, anchor=N, fill=Y)
    #scrollbar = ttk.Scrollbar(right_buttons_panel, orient='vertical', command=middle_screen_panel.yview).pack(side=LEFT, fill=Y)
    i = 1
    dict_firma = {}
    dict_firma["frame0"] = Frame(middle_screen_panel, highlightbackground="black", highlightthickness=0.5)
    dict_firma["frame0"].pack(anchor=N, fill=X)
    e_lp = ttk.Entry(dict_firma["frame0"], width=5)
    e_lp.pack(side=LEFT)
    e_lp.insert(END, "LP")
    e_lp.config(state='disabled')
    e_id = ttk.Entry(dict_firma["frame0"], width=5)
    e_id.pack(side=LEFT)
    e_id.insert(END, "ID")
    e_id.config(state='disabled')
    e_fn = ttk.Entry(dict_firma["frame0"])
    e_fn.pack(side=LEFT)
    e_fn.insert(END, "Imie")
    e_fn.config(state='disabled')
    e_ln = ttk.Entry(dict_firma["frame0"])
    e_ln.pack(side=LEFT)
    e_ln.insert(END, "Nazwisko")
    e_ln.config(state='disabled')
    e_ci = ttk.Entry(dict_firma["frame0"])
    e_ci.pack(side=LEFT)
    e_ci.insert(END, "ID karty")
    e_ci.config(state='disabled')
    for event in sql_result:
        key = str("frame" + str(i))
        dict_firma[key] = Frame(middle_screen_panel, highlightbackground="black", highlightthickness=0.5)
        dict_firma[key].pack(anchor=N, fill=X)
        e = ttk.Entry(dict_firma["frame" + str(i)], width=5)
        e.pack(side=LEFT)
        e.insert(END, str(i))
        e.config(state='disabled')
        for j in range(len(event)):
            if j == 0:
                key = "employee_id" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)], width=5)
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 1:
                key = "employee_fname" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 2:
                key = "employee_lname" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 3:
                key = "employee_cardid" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
                e_btn = ttk.Button(dict_firma["frame" + str(i)], text = "Edytuj", command=lambda employee_id = dict_firma["employee_id" + str(i)].get(): Edit_Employee(employee_id))
                rm_btn = ttk.Button(dict_firma["frame" + str(i)], text = "Usun pracownika", command=lambda employee_id = dict_firma["employee_id" + str(i)].get(), fname = dict_firma["employee_fname" + str(i)].get(), lname = dict_firma["employee_lname" + str(i)].get(): Delete_Employee(employee_id, fname, lname))
                e_btn.pack(side=LEFT)
                rm_btn.pack(side=LEFT)
        i+=1
    main_window.update()
    middle_screen.config(scrollregion=middle_screen.bbox("all"))
def Create_Table_Assingment(sql_result):
    conn = SQL_Connect(connection_params['host'], connection_params['password'], connection_params['ip'], connection_params['database'], connection_params['port'])
    def Generate_Log():
        def Generate_Log_Btn(choosen_dev, choosen_emp, date_from, date_to):
            def Get_Local_Path():
                localpath = os.getcwd()
                if sys.platform.startswith("linux"):
                    dirpath = localpath + "/"
                elif sys.platform == "darwin":
                    print("Jestem maczkiem")
                elif sys.platform == "win32":
                    dirpath = localpath + "\\"
                else:
                    print("Error 112 - nie mozna zdefiniowac wersji systemu")
                return dirpath
            import xlsxwriter, getpass, os, sys

            dirpath = Get_Local_Path()
            usrname = getpass.getuser()
            destination = f'C:\\Users\\{usrname}\\Documents\\AssingmentLog.xlsx'
            date_from = datetime.strptime(date_from, "%m/%d/%y").strftime("%Y-%m-%d") + " 00:00:01"
            date_to = datetime.strptime(date_to, "%m/%d/%y").strftime("%Y-%m-%d") + " 23:59:59"
            sql_query = "SELECT devices.type, devices.rfid_id, employees.fname, employees.lname, assingment.id, assingment.date_withdraw, assingment.date_deposit, assingment.active FROM assingment LEFT JOIN devices ON assingment.device = devices.id LEFT JOIN employees ON assingment.employee = employees.id WHERE assingment.device = " + str(choosen_dev) + " AND assingment.employee = " + str(choosen_emp) + " AND assingment.date_withdraw > '" + date_from + "' AND assingment.date_withdraw < '" + date_to + "'"

            workbook = xlsxwriter.Workbook(destination)
            workbook.add_worksheet("Przypisanie")
            worksheet = workbook.get_worksheet_by_name("Przypisanie")
            worksheet.write(0, 0, "ID wpisu")
            worksheet.write(0, 1, "Urzadzenie")
            worksheet.write(0, 2, "ID Urzadzenia")
            worksheet.write(0, 3, "Imie")
            worksheet.write(0, 4, "Nazwisko")
            worksheet.write(0, 5, "Data pobrania")
            worksheet.write(0, 6, "Data zdania")
            worksheet.write(0, 7, "Aktualnie pobrane (T/N)")

            get_sql_xlsx = conn.cursor()
            get_sql_xlsx.execute(sql_query)
            output = get_sql_xlsx.fetchall()
            #print(output)

            xlsx_row = 0
            for device_type, device_rfid_id, emp_fname, emp_lname, assign_id, assign_dw, assign_dd, assign_act in output:
                try:
                    assign_dw = assign_dw.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(e)
                try:
                    assign_dd = assign_dd.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(e)
                xlsx_row += 1
                worksheet.write(xlsx_row, 0, str(assign_id))
                worksheet.write(xlsx_row, 1, device_type)
                worksheet.write(xlsx_row, 2, device_rfid_id)
                worksheet.write(xlsx_row, 3, emp_fname)
                worksheet.write(xlsx_row, 4, emp_lname)
                worksheet.write(xlsx_row, 5, assign_dw)
                worksheet.write(xlsx_row, 6, assign_dd)
                if assign_act == 0:
                    assign_act = "NIE"
                elif assign_act == 1:
                    assign_act = "TAK"
                worksheet.write(xlsx_row, 7, assign_act)
            
            workbook.close()
            os.system(destination)
                
        newWindow = Toplevel()
        newWindow.title("Wygeneruj log")
        newWindow.geometry("300x200")
        newWindow.iconbitmap(current_directory + "\img\ils.ico")
        
        employees = ["Wszyscy"]
        devices = ["Wszystkie"]
        employees_dict = {}
        devices_dict = {}
        choosen_emp = StringVar()
        choosen_dev = StringVar()
        choosen_emp.set(employees[0])
        choosen_dev.set(devices[0])
        date_from = StringVar()
        date_to = StringVar()
        employees_dict["Wszyscy"] = "assingment.employee"
        devices_dict["Wszystkie"] = "assingment.device"

        temp_emp = Get_SQL_Data("employees", "fname, lname, id", "active", '1')
        for i in range(len(temp_emp)):
            temp_emp_name = temp_emp[i][0] + " " + temp_emp[i][1]
            temp_emp_id = temp_emp[i][2]
            employees.append(temp_emp_name)
            employees_dict[temp_emp_name] = temp_emp_id
        temp_dev = Get_SQL_Data("devices", "type, rfid_id, id", "active", '1')
        for i in range(len(temp_dev)):
            temp_dev_name = temp_dev[i][0] + " (" + temp_dev[i][1] + ")"
            temp_dev_id = temp_dev[i][2]
            devices.append(temp_dev_name)
            devices_dict[temp_dev_name] = temp_dev_id

        #print(devices)

        Label(newWindow, text="Urzadzenie:").grid(row=0, column=0, sticky='ew')
        choose_dev = OptionMenu(newWindow, choosen_dev, *devices)
        choose_dev.grid(row=0, column=1)

        Label(newWindow, text="Pracownik:").grid(row=1, column=0)
        choose_emp = OptionMenu(newWindow, choosen_emp, *employees)
        choose_emp.grid(row=1, column=1)

        Label(newWindow, text="Data OD:").grid(row=2, column=0)
        choose_date1 = DateEntry(newWindow, selectmode='day', width=22, textvariable=date_from)
        choose_date1.grid(row=2, column=1)

        Label(newWindow, text="Data DO:").grid(row=3, column=0)
        choose_date2 = DateEntry(newWindow, selectmode='day', width=22, textvariable=date_to)
        choose_date2.grid(row=3, column=1)

        generate_log_btn_2 = ttk.Button(newWindow, text="Generuj", command=lambda: [Generate_Log_Btn(devices_dict[choosen_dev.get()], employees_dict[choosen_emp.get()], date_from.get(), date_to.get()), newWindow.destroy()]).grid(row=4, column=1)

    Clear(middle_screen_panel)
    Clear(top_buttons_panel)
    #scrollbar = ttk.Scrollbar(right_buttons_panel, orient='vertical', command=middle_screen_panel.yview).pack(side=LEFT, fill=Y)

    i = 1
    dict_firma = {}
    dict_firma["frame0"] = Frame(middle_screen_panel, highlightbackground="black", highlightthickness=0.5)
    dict_firma["frame0"].pack(anchor=N, fill=X)
    e_lp = ttk.Entry(dict_firma["frame0"], width=5)
    e_lp.pack(side=LEFT)
    e_lp.insert(END, "LP")
    e_lp.config(state='disabled')
    e_id = ttk.Entry(dict_firma["frame0"], width=5)
    e_id.pack(side=LEFT)
    e_id.insert(END, "ID")
    e_id.config(state='disabled')
    e_fn = ttk.Entry(dict_firma["frame0"])
    e_fn.pack(side=LEFT)
    e_fn.insert(END, "Imie")
    e_fn.config(state='disabled')
    e_ln = ttk.Entry(dict_firma["frame0"])
    e_ln.pack(side=LEFT)
    e_ln.insert(END, "Nazwisko")
    e_ln.config(state='disabled')
    e_ci = ttk.Entry(dict_firma["frame0"])
    e_ci.pack(side=LEFT)
    e_ci.insert(END, "ID karty pracownika")
    e_ci.config(state='disabled')
    e_dn = ttk.Entry(dict_firma["frame0"])
    e_dn.pack(side=LEFT)
    e_dn.insert(END, "Przypisane urzadzenie")
    e_dn.config(state='disabled')
    e_di = ttk.Entry(dict_firma["frame0"])
    e_di.pack(side=LEFT)
    e_di.insert(END, "ID urzadzenia")
    e_di.config(state='disabled')
    e_dt = ttk.Entry(dict_firma["frame0"])
    e_dt.pack(side=LEFT)
    e_dt.insert(END, "Data wypozyczenia")
    e_dt.config(state='disabled')
    generate_log_btn = ttk.Button(top_buttons_panel, text="Generuj\nlogi", command=lambda: Generate_Log()).pack(side=TOP, anchor=N, fill=Y)
    for event in sql_result:
        key = str("frame" + str(i))
        dict_firma[key] = Frame(middle_screen_panel)
        dict_firma[key].pack(anchor=N, fill=X)
        e = ttk.Entry(dict_firma["frame" + str(i)], width=5)
        e.pack(side=LEFT)
        e.insert(END, str(i))
        e.config(state='disabled')
        for j in range(len(event)):
            if j == 0:
                key = "assingment_id" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)], width=5)
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 1:
                key = "employee_fname" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 2:
                key = "employee_lname" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 3:
                key = "employee_cardid" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 4:
                key = "device_name" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 5:
                key = "device_rfidid" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
            elif j == 6:
                key = "date" + str(i)
                dict_firma[key] = StringVar(middle_screen_panel)
                dict_firma[key].set(event[j])
                e = ttk.Entry(dict_firma["frame" + str(i)])
                e.pack(side=LEFT)
                e.insert(END, dict_firma[key].get())
                e.config(state='disabled')
              
        i+=1
    main_window.update()
    middle_screen.config(scrollregion=middle_screen.bbox("all"))

#Communicate at bottom informing about state of device
main_communicate = StringVar()
main_communicate.set("Wszystko OK, czekam na skan.")
#main_communicate.set("asdasdasdasdasdasdasd")

#Label for main communicate
main_communicate_label = ttk.Label(main_window, text=main_communicate.get(), anchor=CENTER, font=("Arial", 15))
main_communicate_label.pack(side=BOTTOM, fill=X)

#########################################
#BUTTONS AND WINDOWS SECTION
#LEFT PANEL BUTTONS
main_button = ttk.Button(left_buttons_panel, text="     Panel\nprzypisania", command=lambda: Create_Table_Assingment(Get_Assingment())).pack(side=TOP, anchor=NW, fill=X)

def DB_Data_Window():
    newWindow = Toplevel()
    newWindow.title("Podaj parametry polaczenia z baza danych")
    newWindow.geometry("250x380")
    newWindow.iconbitmap(current_directory + "\img\ils.ico")

    ip = StringVar()
    host = StringVar()
    password = StringVar()
    database = StringVar()
    port = StringVar()

    serial = StringVar()
    baudrate = StringVar()
    datasize = StringVar()
    parity = StringVar()

    ip.set(str(connection_params['ip']))
    host.set(str(connection_params['host']))
    password.set(str(connection_params['password']))
    database.set(str(connection_params['database']))
    port.set(str(connection_params['port']))

    serial.set(str(serial_params['com']))
    baudrate.set(str(serial_params['baud']))
    datasize.set(str(serial_params['datasize']))
    parity.set(str(serial_params['parity']))

    serials = []
    baudrates = ["600", "1200", "2400", "4800", "9600", "14400", "19200", "38400", "56000", "57600", "115200"]
    datasizes = ["7", "8"]
    parities = ["none", "even", "odd", "mark"]
    for i in range(0, 21):
        serials.append("COM" + str(i))
    #print(serials)

    ttk.Label(newWindow, text="Baza:", anchor=E, font=("Arial", 15)).grid(column=0, row=0)
    ttk.Label(newWindow, text="-------------", anchor=E, font=("Arial", 15)).grid(column=1, row=0)
    ttk.Label(newWindow, text="IP:", anchor=E, font=("Arial", 15)).grid(column=0, row=1)
    ttk.Label(newWindow, text="Login:", anchor=E, font=("Arial", 15)).grid(column=0, row=2)
    ttk.Label(newWindow, text="Haslo:", anchor=E, font=("Arial", 15)).grid(column=0, row=3)
    ttk.Label(newWindow, text="Baza:", anchor=E, font=("Arial", 15)).grid(column=0, row=4)
    ttk.Label(newWindow, text="Port:", anchor=E, font=("Arial", 15)).grid(column=0, row=5)
    ttk.Label(newWindow, text="RFID:", anchor=E, font=("Arial", 15)).grid(column=0, row=6)
    ttk.Label(newWindow, text="-------------", anchor=E, font=("Arial", 15)).grid(column=1, row=6)
    ttk.Label(newWindow, text="COM:", anchor=E, font=("Arial", 15)).grid(column=0, row=7)
    ttk.Label(newWindow, text="Baudrate:", anchor=E, font=("Arial", 15)).grid(column=0, row=8)
    ttk.Label(newWindow, text="Datasize:", anchor=E, font=("Arial", 15)).grid(column=0, row=9)
    ttk.Label(newWindow, text="Parity:", anchor=E, font=("Arial", 15)).grid(column=0, row=10)
    ttk.Label(newWindow, text="-------------", anchor=E, font=("Arial", 15)).grid(column=1, row=11)

    Entry(newWindow, textvariable=ip).grid(column=1, row=1)
    Entry(newWindow, textvariable=host).grid(column=1, row=2)
    Entry(newWindow, textvariable=password).grid(column=1, row=3)
    Entry(newWindow, textvariable=database).grid(column=1, row=4)
    Entry(newWindow, textvariable=port).grid(column=1, row=5)
    OptionMenu(newWindow, serial, *serials).grid(column=1, row=7)
    OptionMenu(newWindow, baudrate, *baudrates).grid(column=1, row=8)
    OptionMenu(newWindow, datasize, *datasizes).grid(column=1, row=9)
    OptionMenu(newWindow, parity, *parities).grid(column=1, row=10)
    

    def Button_Command(ip, host, password, database, port, window):
        path = Get_Local_Path()
        db_file = open(path + "\db\db_params.txt", 'w')
        db_file.write('ip="' + ip.get() + '"\nhost="' + host.get() + '"\ndatabase="' + database.get() + '"\npassword="' + password.get() + '"\nport="' + port.get() + '"' )
        db_file.close()
        db_file = open(path + "\db\ser_params.txt", 'w')
        db_file.write('serial="' + serial.get() + '"\nbaudrate="' + baudrate.get() + '"\ndatasize="' + datasize.get() + '"\nparity="' + parity.get() + '"' )
        db_file.close()
        window.destroy()

    ttk.Button(newWindow, text="Aktualizuj", command=lambda: Button_Command(ip, host, password, database, port, newWindow)).grid(column=1, row=12)
db_data_button = ttk.Button(left_buttons_panel, text="Ustawienia\npolaczenia", command=lambda: DB_Data_Window()).pack(side=TOP, anchor=NW, fill=X)

#TOP PANEL BUTTONS

#RIGHT PANEL BUTTONS
employees_button = ttk.Button(right_buttons_panel, text="    Zarzadzaj\npracownikami", command=lambda: Create_Table_Employees(Get_Employees())).pack(side=TOP, anchor=NW, fill=X)

devices_button = ttk.Button(right_buttons_panel, text="    Zarzadzaj\nurzadzeniami", command=lambda: Create_Table_Devices(Get_Devices())).pack(side=TOP, anchor=NW, fill=X)

#MIDDLE SCREEN

if connection_params == None:
    Update_Label(main_communicate_label, main_communicate, "Nieprawidlowe dane polaczenia z baza danych.\nUzupelnij dane i zresetuj aplikacje.", "red")
else:
    try:
        conn = SQL_Connect(connection_params['host'], connection_params['password'], connection_params['ip'], connection_params['database'], connection_params['port'])
    except Exception as e:
        Update_Label(main_communicate_label, main_communicate, "Blad polaczenia z baza danych.\n" + str(e), "red")



lbl = Label(main_window, compound='top', font = ('calibri', 45, 'bold'))
lbl.pack(anchor='center')

Read_Serial()
main_window.mainloop()