"""OSATerminal.py:
A Simple raw terminal interface to send/receive
raw SCPI commands to/from the OSA
Depends on AQ6380Controls library
Depends on pyvisa
Depends on pyvisa-py as visa interface
To get dependencies,
pip install pyvisa
pip install pyvisa-py
To run: python OSATerminal.py or py OSATerminal.py depending on system
"""
from AQ6380Controls import AQ6380Controls
osaaddr='192.168.1.177'
if __name__=='__main__':
    osa=AQ6380Controls(osaaddr)#Set up AQ6380Controls object
    osa.open()
    while True:
        #Poll command line for command and then send it to the OSA
        cmd=input('Enter Command: ')#Obtain command
        if cmd.upper()=='EXIT':#Exit command; exit application
            exit(0)
            
        print(osa.sendSCPI(cmd))#Run command and print return value