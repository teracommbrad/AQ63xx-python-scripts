"""OSACommandLine.py:
A Simple Command-line interface for the AQ6380 OSA
Depends on AQ6380Controls library
Depends on pyvisa
Depends on pyvisa-py as visa interface
To get dependencies,
pip install pyvisa
pip install pyvisa-py
To run: python OSACommandLine.py or py OSACommandLine.py depending on system
"""
from AQ6380Controls import AQ6380Controls, sensitivities

cmdlist="""Command list:
CENTER val: Sets the center in nm
    Example:  "CENTER 1608"
PEAKWLEN: Gets peak wavelength
PEAKPOWER: Gets peak power
RES val (in nm)
    Example: "RES 0.005"
SAVE Filename: Gets data and saves to filename as csv
    Example: "SAVE testres.csv"
SCPI CMD: Sends a SCPI command to the OSA
    Example: "SCPI :calc:mark:max"
SENS NAME
    Example: "SENS MID"
SPAN val: Sets span in nm
    Example: "SPAN 10"
SPEED 1x or 2x
    Example: "SPEED 1x"
START: Starts a measurement.  Will not allow another command until measurement is complete

EXIT: Exits the command line
Commands are not case sensitive
"""

osaaddr='192.168.1.177'#Set OSA Address
if __name__=='__main__':
    osa=AQ6380Controls(osaaddr)
    osa.open()#Open connection to OSA
    while True:
        cmd=input('Enter Command: ')#Obtain command and split it
        splitcmd=cmd.strip().split()
        basecmd=splitcmd[0].upper()#Get base command from split command
        if basecmd=='HELP':
            #Help command; print help
            print(cmdlist)
        elif basecmd=='SENS':
            #Check and set sensitivity
            sensval=splitcmd[1].upper()
            if sensval not in sensitivities:#Invalid sensitivity
                print(f'Sensitivity of {sensval} is invalid')
            else:
                osa.setSensitivity(sensval)
        elif basecmd=='RES':
            #Set Resolution in nm
            resolutionval=splitcmd[1]
            osa.setResolution(resolutionval)
        elif basecmd=='SPEED':
            #Set Speed 1x or 2x
            osa.setSweepSpeed(splitcmd[1])
        elif basecmd=='CENTER':
            #Set center (nm)
            osa.setCenter(splitcmd[1])
        elif basecmd=='SPAN':
            #Set span (nm)
            osa.setSpan(splitcmd[1])
        elif basecmd=='START':
            #Start sweep
            osa.singleSweep()
        elif basecmd=='PEAKWLEN':
            #Get Peak Wavelength
            print(round(float(osa.getPeakWavelength()), 3))
        elif basecmd=='PEAKPOWER':
            #Get Peak Power
            print(osa.getPeakPower())
        elif basecmd=='SCPI':
            #SCPI Command
            scpicmd=' '.join(splitcmd[1:])
            print(osa.sendSCPI(scpicmd))
        elif basecmd=='SAVE':
            #Save trace as CSV to file
            (xvals, yvals)=osa.getTraceVals()
            filename=splitcmd[1]
            with open(filename, 'w') as fp:
                #Open file
                for idx in range(len(xvals)):
                    #Save CSV line by line
                    fp.write(f'{xvals[idx]},{yvals[idx]}\n')
        elif basecmd=='EXIT':
            #Exit application
            exit(0)
        else:#Invalid Command
            print('Invalid Command: Valid Commands are:')
            print(cmdlist)