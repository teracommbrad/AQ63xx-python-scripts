"""OSAGUIv2.py
A GUI interface for the AQ6380 OSA that includes graphing
Depends on AQ6380Controls library
Depends on pyvisa, pyvisa-py, and matplotlib
To get dependencies,
pip install pyvisa
pip install pyvisa-py
pip install matplotlib
To run:
python OSAGUIv2.py or py OSAGUIv2.py depending on system
This, along with the pip install commands should be done in a virtual environment
"""
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import asksaveasfile
from AQ6380Controls import *
import time
import threading
import matplotlib.pyplot as plt

#default TKinter Settings
stickall='news'
DEFAULT_PAD_X=5
DEFAULT_PAD_Y=5

osaBusy=threading.Event()#OSA Busy Event

def write_text_box(textbox, str):
    """write_text_box: Writes a string to a TKinter textbox
    INPUTS:
    textbox (tkinter.Text): The text box to write to
    str (string): The string to write"""
    textbox.config(state=tk.NORMAL)#Write enable text box
    textbox.delete("1.0", "end")#Remove all text
    textval=str.strip()#Strip ends of string
    textbox.insert('1.0', str)#Write string to text box
    textbox.update()#Force update text box
    textbox.config(state=tk.DISABLED)#Write disable text box
    
def connect_to_osa():
    """connect_to_osa: Retrieves inputs from GUI 
    and tries to connect to OSA
    Does not try to connect if OSA connection is busy"""
    if osaBusy.is_set():#If OSA busy
        write_text_box(textbox, 'OSA Busy Error')
        print("OSA busy. Exiting function")
        return
    osaBusy.set()#Set event osaBusy
    ipaddr=ipentry.get()#Get ip address from dialog and set the OSA's IP address
    osa.setAddress(ipaddr)
    try:
        write_text_box(textbox, 'Connecting to OSA')
        osa.open()#Try to open OSA
    except Exception as e:#Exception
        write_text_box(textbox, f'Cannot Connect to OSA: error {e}')#Print error to text box
        connectedlabel.config(text='Not Connected', bg='red3')#Red label
    else:#Connected
        connectedlabel.config(text='Connected', bg='green3')#Set green label
        write_text_box(textbox, 'Connected to OSA')#Write connected to OSA
    finally:
        osaBusy.clear()#Clear event

def getSensitivities():
    """getSensitivities: Compile a list of valid sensitivities and return it
    RETURNS:
    A list of valid sensitivities"""
    sensitivityvals=[]
    for x in tradSensitivities:#Compile (x2) and regular (x1) traditional sensitivities and dBm levels
        sensitivityvals.append(x+' '+str(dBmFromSensitivity(x))+' dBm')
        sensitivityvals.append(f'{x}(x2) '+str(dBmFromSensitivity(f'{x}(x2)'))+' dBm')
    sensitivityvals+=[x+' '+str(dBmFromSensitivity(x))+' dBm' for x in rapidSensitivities]#Add rapid sensitivities to list
    return sensitivityvals

def sweepButtonPressed():
    """sweepButtonPressed: Retrieves input from GUI and performs a single sweep
    Does not perform sweep if OSA is not connected or is busy"""
    if not osa.connected:#OSA Not Connected
        write_text_box(textbox, 'OSA Not Connected Error')
        return
    if osaBusy.is_set():#OSA busy
        write_text_box(textbox, 'OSA Busy Error')
        print("OSA busy. Exiting function")
        return
    osaBusy.set()#Set OSA busy event
    write_text_box(textbox, 'Performing Sweep')
    sensitivityspeed=sensitivityentry.get()#Get sensitivity and speed value from GUI
    if '(x2)' in sensitivityspeed:#Set sweep speed, 1x or 2x
        osa.setSweepSpeed('2x')
    else:
        osa.setSweepSpeed('1x')
    basesensitivity=sensitivityspeed.split('(')[0].split(' ')[0]#Get sensitivity name
    osa.setSensitivity(basesensitivity)
    osa.setCenter(centerentry.get())#Get center from GUI and set it
    osa.setSpan(spanentry.get())#Get span from GUI and set it
    osa.setResolution(resolutionentry.get())#Get resolution from GUI and set it
    osa.singleSweep()#Perform single sweep and print peak power and peak wavelength to text box
    write_text_box(textbox, f'Peak Power: {round(osa.getPeakPower(), 3)} dBm\nPeak Wavelength: {round(osa.getPeakWavelength(), 3)} nm')
    osaBusy.clear()#Clear OSA busy event

def save_sweep_data():
    """save_sweep_data: Brings up save file dialog to select file name
    and then saves sweep data to chosesn CSV file
    Does not save sweep data if OSA is not connected or is busy
    """
    if not osa.connected:#Not Connected
        write_text_box(textbox, 'OSA Not Connected Error')
        return
    f=asksaveasfile(initialfile='untitled.csv', defaultextension='.csv', filetypes=[('Commma Separated','*.csv')])#Get file name to save to
    if f is None:#No valid file name, exit function
        return
    if osaBusy.is_set():#OSA Busy
        write_text_box(textbox, 'OSA Busy Error')
        print("OSA busy. Exiting function")
        return
    osaBusy.set()#Set OSA busy event
    (xvals, yvals)=osa.getTraceVals()#Get trace vals (xvals, yvals)
    osaBusy.clear()#Clear OSA busy event
    for idx in range(len(xvals)):#Get x and y vals into CSV format and write to file
        f.write(f'{xvals[idx]},{yvals[idx]}\n')
    f.close()

def openPlotWindow():
    """openPlotWindow:
    Opens a plot window with the OSA sweep data
    Does not perform sweep if OSA is not connected or is busy
    """
    if not osa.connected:
        write_text_box(textbox, 'OSA Not Connected Error')
        return
    if osaBusy.is_set():#OSA Busy
        write_text_box(textbox, 'OSA Busy Error')
        print("OSA busy. Exiting function")
        return
    osaBusy.set()#Set OSA busy event
    (xvals, yvals)=osa.getTraceVals()#Get trace vals (xvals, yvals)
    osaBusy.clear()#Clear OSA busy event
    fig1, ax1=plt.subplots()#Set up plot window
    ax1.plot(xvals, yvals)
    ax1.set_xlabel('Wavelength (nm)')
    ax1.set_ylabel('Amplitude (dBm)')
    ax1.set_title('Amplitude vs wavelength')
    plt.show()#Show plot window

if __name__=='__main__':
    sensitivityvals=getSensitivities()#Compile list of sensitivities
    osa=AQ6380Controls()
    #Set up tkinter window
    window=tk.Tk()#Set up tkinter window
    window.title('AQ6380 Controls')
    window.geometry('600x400')

    #Frame inside window for responsive interface; widgets are put in a grid inside frame
    frame=tk.Frame(window)

    #Set up widgets
    ipaddrlabel=tk.Label(frame, text='IP Address')#IP Address label
    ipaddrlabel.grid(row=0, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    ipentry=tk.Entry(frame, width=18)#IP address entry
    ipentry.grid(row=0, column=1, columnspan=2, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    connectedlabel=tk.Label(frame, text='Not Connected', bg='red3', width=14)#Is connected label
    connectedlabel.grid(row=0, column=3, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    connectbutton=tk.Button(frame, text='Connect', command=lambda: threading.Thread(target=connect_to_osa).start())#Connect button
    connectbutton.grid(row=1, column=0, columnspan=2, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    centerlabel=tk.Label(frame, text='Center WL (nm)')#Center wavelength label
    centerlabel.grid(row=2, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    centerentry=tk.Entry(frame, width=12)#Center wavelength entry
    centerentry.grid(row=2, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    spanlabel=tk.Label(frame, text='Span (nm)')#Span (nm) label
    spanlabel.grid(row=2, column=2, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    spanentry=tk.Entry(frame, width=12)#Span entry
    spanentry.grid(row=2, column=3, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    resolutionlabel=tk.Label(frame, text='Resolution (nm)')#Resolution label
    resolutionlabel.grid(row=3, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    resolutionentry=ttk.Combobox(frame, width=12, values=resolutions)#Resolution entry as dropdown, resolutions from AQ6380Controls.resolutions
    resolutionentry.current(0)#Set default resolution entry
    resolutionentry.grid(row=3, column=1, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    sensitivitylabel=tk.Label(frame, text='Sensitivity')#Sensitivity label
    sensitivitylabel.grid(row=3, column=2, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    sensitivityentry=ttk.Combobox(frame, width=20, values=sensitivityvals)#Sensitivity entry as dropdown, values from list of sensitivities
    sensitivityentry.current(0)#Set default sensitivity value
    sensitivityentry.grid(row=3, column=3, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    singlesweepbutton=tk.Button(frame, text='Single Sweep', command=lambda: threading.Thread(target=sweepButtonPressed).start())#Start Sweep Button
    singlesweepbutton.grid(row=4, column=0, sticky=stickall, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y)
    textbox=tk.Text(frame,  width=40, height=10, state=tk.DISABLED)#Text box to be written to by program
    textbox.grid(row=5, column=0, columnspan=4, sticky=stickall, pady=10, padx=10)
    write_text_box(textbox, 'Not Connected')
    savesweepbutton=tk.Button(frame, text='Save CSV', command=lambda: save_sweep_data())#Save Sweep Data as CSV button
    savesweepbutton.grid(row=6, column=0, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y, sticky=stickall)
    plotbutton=tk.Button(frame, text='Plot OSA Data', command=lambda: openPlotWindow())#Save Sweep Data as CSV button
    plotbutton.grid(row=6, column=1, padx=DEFAULT_PAD_X, pady=DEFAULT_PAD_Y, sticky=stickall)
    frame.pack()
    window.protocol('WM_DELETE_WINDOW', lambda:exit(0))
    window.mainloop()#Run main loop