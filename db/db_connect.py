import mysql.connector as database
import serial

def SQL_Connect(dbLogin, dbPassword, dbHost, dbDatabase, dbPort):
    global conn
    conn = database.connect(user = dbLogin, password = dbPassword, host = dbHost, database = dbDatabase, port = dbPort)
    return conn

def Serial_Connect(_serial, _baudrate, _datasize, ser_parity):
    if ser_parity == 'none':
        ser_parity = serial.PARITY_NONE
    elif ser_parity == 'even':
        ser_parity = serial.PARITY_EVEN
    elif ser_parity == 'odd':
        ser_parity = serial.PARITY_ODD
    elif ser_parity == 'mark':
        ser_parity = serial.PARITY_MARK

    if _datasize == '7':
        _datasize = serial.SEVENBITS
    elif _datasize == '8':
        _datasize = serial.EIGHTBITS

    ser = serial.Serial(
        port=_serial,
        baudrate=int(_baudrate),
        parity=ser_parity,
        stopbits=serial.STOPBITS_ONE,
        bytesize=_datasize,
        timeout=0.2,
        write_timeout=0.2,
    )
    return ser

def Get_Employees():
    global conn
    sql_query = "SELECT id, fname, lname, card_id FROM employees WHERE active = 1 ORDER BY lname"
    get_sql = conn.cursor()
    get_sql.execute(sql_query)
    output = get_sql.fetchall()
    return output

def Get_Devices():
    global conn
    sql_query = "SELECT id, type, rfid_id FROM devices WHERE active = 1 ORDER BY type"
    get_sql = conn.cursor()
    get_sql.execute(sql_query)
    output = get_sql.fetchall()
    return output

def Get_Assingment():
    global conn
    sql_query = "SELECT assingment.id, employees.fname, employees.lname, employees.card_id, devices.type, devices.rfid_id, assingment.date_withdraw FROM assingment LEFT JOIN employees ON employees.id = assingment.employee LEFT JOIN devices ON devices.id = assingment.device WHERE assingment.active = 1 ORDER BY date_withdraw DESC"
    get_sql = conn.cursor()
    get_sql.execute(sql_query)
    output = get_sql.fetchall()
    return output

def Update_SQL_Data_Prepared(prepared_query):
    update_sql = conn.cursor()
    update_sql.execute(prepared_query)
    conn.commit()

def Get_SQL_Data(table, what, where, where2):
    global conn
    sql_query = "SELECT " + what + " FROM " + table + " WHERE " + where + " = '" + where2 + "'"
    print(sql_query)
    get_sql = conn.cursor()
    get_sql.execute(sql_query)
    output = get_sql.fetchall()
    return output