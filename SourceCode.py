
import PySimpleGUI as sg

import sys
import os
from zk import ZK, const
import pyodbc
from datetime import datetime
import os
import schedule
import time
import _thread



def push_date(values=None, Thread=True):
    if values == None:
        values = sg.user_settings_load()

    log = os.path.join(os.environ['USERPROFILE'])  + '\log.txt'
    conn = None
    # create ZK instance
    zk = ZK(values['-IP-'], port=int(values['-Port-']), timeout=5, password=values['-Password-'], force_udp=False, ommit_ping=False)
    try:
        # connect to device
        conn = zk.connect()
        # disable device, this method ensures no activity on the device while the process is run
        conn.disable_device()
        # another commands will be here!
        # Example: Get All Users
        attendances = conn.get_attendance()
        cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=localhost;DATABASE=Attendance;UID=sa;PWD=02AMNDr.Z_0')
        cursor = cnxn.cursor()


        count = 0
        for attendance in attendances:
            cursor.execute(
                "select * from attendance Where employeeid=? and eventtime=?",
                attendance.user_id,
                attendance.timestamp
            )

            rows = cursor.fetchall()
            if len(rows) == 0:
                cursor.execute(
                    "Insert Into attendance(employeeid, eventtime, isCheckIn, donwloaddate) Values(?, ?, ?, ?)",
                    attendance.user_id,
                    attendance.timestamp,
                    attendance.punch,
                    datetime.now()
                )
            if count % 100 == 0:
                cnxn.commit()
            print(f'{attendance.user_id},{attendance.punch},{attendance.status}, {attendance.timestamp}, {attendance.uid}')
            
        cnxn.commit()
        # Test Voice: Say Thank You
        conn.test_voice()
        # re-enable device after all commands already executed
        conn.enable_device()
        with open(log,'a') as f:
            f.write(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}: All attendance data uploaded successfully\n')
        
        if not Thread:
            sg.Print(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}: All attendance data uploaded successfully\n')
    except Exception as e:
        print ("Process terminate : {}".format(e))
        with open(log,'a') as f:
            f.write(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}: {e}\n')
        
        if not Thread:
            sg.Print(f'{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}: {e}\n')

        
    finally:
        if conn:
            conn.disconnect()

def new_thread():
    print("new Thread")
    global running
    global first_time
    times = sg.user_settings_get_entry('-Time-', '')
    if first_time and times != '':
        for run_time in times.split(","):
            print(run_time)
            schedule.every().day.at(run_time).do(push_date)
        first_time = False
    elif times != '':
        for run_time in times.split(","):
            schedule.every().day.at(run_time).do(push_date)
    else:
        schedule.every(3).hour.do(push_date)

    running = True
    while running:
        # print("running", datetime.now())
        schedule.run_pending()
        time.sleep(0.1)

sg.theme('SandyBeach')      

# All the stuff inside your window.
layout = [  [sg.Text('Push Attendance Details')],
            [sg.Text('IP', size=(15,1)), sg.InputText(sg.user_settings_get_entry('-IP-', '') , disabled=True, key='-IP-')],
            [sg.Text('Port', size=(15,1)), sg.InputText(sg.user_settings_get_entry('-Port-', ''),disabled=True,   key='-Port-')],
            [sg.Text('Password', size=(15,1)), sg.InputText(sg.user_settings_get_entry('-Password-', ''),disabled=True,   key='-Password-')],
            [sg.Text('Run Time', size=(15,1)), sg.InputText(sg.user_settings_get_entry('-Time-', ''),disabled=True,   key='-Time-')],
            [sg.Button('Save'), sg.Button('Run'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Upload FBR to Server', layout, finalize=True)
window.bind("<Control-Alt-KeyPress-z>", "CTRL-Z")

# Event Loop to process "events" and get the "values" of the inputs
first_time = True
while True:
    _thread.start_new_thread(new_thread, ())
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':	# if user closes window or clicks cancel
      break
    elif event == 'Save':
        sg.user_settings_set_entry('-IP-', values['-IP-'])
        sg.user_settings_set_entry('-Port-', values['-Port-'])
        sg.user_settings_set_entry('-Password-', values['-Password-'])
        sg.user_settings_set_entry('-Time-', values['-Time-'])
        sg.popup("You Settings Has been Saved")
    elif event == 'CTRL-Z':
        window['-IP-'].update(disabled=False)
        window['-Port-'].update(disabled=False)
        window['-Password-'].update(disabled=False)
        window['-Time-'].update(disabled=False)
    elif event == 'Run':
        push_date(values, Thread=False)



window.close()
