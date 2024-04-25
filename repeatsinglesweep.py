"""OSATerminal.py:
A Simple raw terminal interface to send/receive
raw SCPI commands to/from the OSA
Depends on AQ6380Controls library
Depends on pyvisa
Depends on pyvisa-py as visa interface
To get dependencies,
pip install pyvisa
pip install pyvisa-py
To run: python repeatsinglesweep.py or py repeatsinglesweep.py depending on system
"""
from AQ6380Controls import AQ6380Controls
osaaddr='192.168.1.177'#Change to whatever the OSA's ip address is
filename='tracedata.csv'#Change to the desired file name to save trace to

if __name__=='__main__':
    osa=AQ6380Controls(osaaddr)
    osa.open()#Open connection to OSA
    #Any other startup code (i.e. setting sensitivity or span) should be put here
    while True:
        osa.singleSweep()#Single Sweep; waits for end "1"
        (xvals, yvals)=osa.getTraceVals()#Get trace
        with open(filename, 'w') as fp:#Save trace to file
            #Open file
            for idx in range(len(xvals)):
                #Save CSV line by line
                fp.write(f'{xvals[idx]},{yvals[idx]}\n')
        print("Trace complete")

        
        