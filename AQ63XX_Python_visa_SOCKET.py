#
# Yokogawa AQ63XX OSA sample program (PyVISA)
# Remote Interface = ETHERNET(SOCKET)
#
# This sample program requires pyvisa.
#
# AQ63XX Setting: [SYSTEM]<REMOTE INTERFACE> = "NETWORK(SOCKET)"
#
#NOTE: 11/20/2023 Used pyvisa-py for VISA library
import pyvisa

osaaddr='192.168.1.177'

    
    
def left(text, n):
    return text[:n]

def getPeakWavelength(osa):
    return osa.query(":calc:cat swth; :calc; :calc:data?").split(',')[0]
if '__main__' == __name__: # execute only if run as a script

    # open O SA
    rm = pyvisa.ResourceManager()
    osa = rm.open_resource(f"TCPIP::{osaaddr}::10001::SOCKET")
    osa.read_termination = '\n'
    osa.write_termination = '\n'

    # Open OSA
    a = osa.query("open \"anonymous\"")     # send username & get strings
    print(a)
    a = osa.query("aaa")                    # send password & get "ready" strings
    print(a)

    # Get *IDN query
    a = osa.query("*IDN?")
    print(a)

    # Set command mode = AQ637X/AQ638X mode
    #osa.write('*RST')
    osa.write("CFORM1")
    a = osa.query("*IDN?")
    print(a)
    # single sweep
    #osa.write()
    osa.write(':sens:wav:cent 1608nm')#Set center to 1608 nm
    osa.write(':sens:wav:span 20nm')#Set span to 10nm
    osa.write(':init:smode 1')#Single Sweep Mode
    osa.write("*CLS")
    osa.write(':init')
    #wait until sweep complete
    while True:
        a = osa.query(":stat:oper:even?")
        if left(a,1) == "1":
            break
    print("sweep complete")
    osa.write(':calc:mark:max')
    # Measure spectrum width
    peakpowerdata= osa.query(":calc:cat pow; :calc; :calc:data?").split(',')
    print(peakpowerdata)
    # close osa
    osa.close()
