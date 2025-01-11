
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

    if sg.user_settings_get_entry('-Folder-') != '':
        log = sg.user_settings_get_entry('-Folder-')
    else:
        log = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    log = log + '\log.txt'
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


        for attendance in attendances:
            cursor.execute(
                "select * from attendance Where employeeid=? and eventtime=?",
                attendance.user_id,
                attendance.timestamp
            )

            rows = cursor.fetchall()
            if len(rows) == 0 and attendance.user_id != 1:
                cursor.execute(
                    "Insert Into attendance(employeeid, eventtime, isCheckIn, donwloaddate) Values(?, ?, ?, ?)",
                    attendance.user_id,
                    attendance.timestamp,
                    attendance.punch,
                    datetime.now()
                )
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
    if first_time:
        print("first time")
        schedule.every(1).hour.do(push_date)
        first_time = False
    running = True
    while running:
        print("running", datetime.now())
        schedule.run_pending()
        time.sleep(0.1)


# All the stuff inside your window.
layout = [  [sg.Text('Push Attendance Details')],
            [sg.Text('Folder'), sg.In(sg.user_settings_get_entry('-Folder-', ''), size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Text('IP'), sg.InputText(sg.user_settings_get_entry('-IP-', ''), key='-IP-')],
            [sg.Text('Port'), sg.InputText(sg.user_settings_get_entry('-Port-', ''), key='-Port-')],
            [sg.Text('Password'), sg.InputText(sg.user_settings_get_entry('-Password-', ''), key='-Password-')],
            [sg.Button('Save'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Upload FBR to Server', layout, finalize=True)
window.bind("<Control-KeyPress-t>", "CTRL-T")

# Event Loop to process "events" and get the "values" of the inputs
first_time = True
while True:
    _thread.start_new_thread(new_thread, ())
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':	# if user closes window or clicks cancel
      break
    elif event == 'Save':
        sg.user_settings_set_entry('-Folder-', values['-FOLDER-'])
        sg.user_settings_set_entry('-IP-', values['-IP-'])
        sg.user_settings_set_entry('-Port-', values['-Port-'])
        sg.user_settings_set_entry('-Password-', values['-Password-'])
        sg.popup("You Settings Has been Saved")
        push_date(values, Thread=False)

    elif event == "CTRL-T":
        pass
        # window.UnHide()
        # window.maximize()
       

window.close()
