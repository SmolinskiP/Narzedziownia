import re
from fnct.getpath import Get_Local_Path

def Connection_Dict():
    path = Get_Local_Path()
    db_file = open(path + "\db\db_params.txt", 'r')
    db_params = db_file.readlines()
    connection_dict = {}

    connection_dict['ip'] = re.findall(r'"([^"]*)"', db_params[0])[0]
    connection_dict['host'] = re.findall(r'"([^"]*)"', db_params[1])[0]
    connection_dict['database'] = re.findall(r'"([^"]*)"', db_params[2])[0]
    connection_dict['password'] = re.findall(r'"([^"]*)"', db_params[3])[0]
    connection_dict['port'] = re.findall(r'"([^"]*)"', db_params[4])[0]

    print(connection_dict['ip'])
    
    if connection_dict['ip'] == "":
        return None
    elif connection_dict['host'] == "":
        return None
    elif connection_dict['database'] == "":
        return None
    elif connection_dict['password'] == "":
        return None
    elif connection_dict['port'] == "":
        return None
    else:
        return connection_dict
    db_file.close()



def Serial_Dict():
    path = Get_Local_Path()
    ser_file = open(path + "\db\ser_params.txt", 'r')
    ser_params = ser_file.readlines()
    serial_dict = {}

    serial_dict['com'] = re.findall(r'"([^"]*)"', ser_params[0])[0]
    serial_dict['baud'] = re.findall(r'"([^"]*)"', ser_params[1])[0]
    serial_dict['datasize'] = re.findall(r'"([^"]*)"', ser_params[2])[0]
    serial_dict['parity'] = re.findall(r'"([^"]*)"', ser_params[3])[0]

    
    if serial_dict['com'] == "":
        return None
    elif serial_dict['baud'] == "":
        return None
    elif serial_dict['datasize'] == "":
        return None
    elif serial_dict['parity'] == "":
        return None
    else:
        return serial_dict
    db_file.close()