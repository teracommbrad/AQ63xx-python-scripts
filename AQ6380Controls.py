"""AQ6380Controls Library
Depends on pyvisa, pyvisa-py as visa interface
To get dependencies,
pip install pyvisa
pip install pyvisa-py
"""
import pyvisa
import re
#Constants
sensitivities=['NHLD', 'NAUT',  'MID', 'HIGH1', 'HIGH2', 'HIGH3', 'NORM', 'RAPID1', 'RAPID2','RAPID3',
               'RAPID4', 'RAPID5', 'RAPID6']#Sensitivities indexed by code

fixedSensitivities=['NORM', 'MID', 'HIGH1', 'HIGH2', 'HIGH3', 'RAPID1', 'RAPID2','RAPID3',
               'RAPID4', 'RAPID5', 'RAPID6']
tradSensitivities=['NORM', 'MID', 'HIGH1', 'HIGH2', 'HIGH3']
rapidSensitivities=['RAPID1', 'RAPID2', 'RAPID3', 'RAPID4', 'RAPID5', 'RAPID6']
resolutions=['0.005', '0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2']
sweepSpeeds=['1x', '2x']

def dBmFromSensitivity(sens, speed=None):
    """dBmFromSensitivity:
    Returns the dBm value from a given sensitivity and speed, -1 if invalid
    Case 1: Sensitivity and speed given:
        sens (str): The sensitivity value
        speed (str) '1x' of 'x1' or '2x' or 'x2' not case sensitive:
                    The speed value
    Case 2: Sensitivity given without speed:
        sens (str): The sensitivity value
         The speed is read by extracting 2x from the sensitivity value
          Valid sensitivity values are "x(2x)" or "x"
          where x is a valid sensitivity level
            """
    sens=sens.upper()#
    tradMode=False
    senssplit=sens.split('(')
    sensbase=senssplit[0]
    if sensbase not in fixedSensitivities:
        print('Invalid Sensitivity')#Invalid sensitivity; exit function
        return -1
    #Check for traditional sensitivities which may have x1 or x2 speed
    if sensbase=='NORM':
        tradMode=True
        dbmval=-62
    elif sensbase=='MID':
        tradMode=True
        dbmval=-67
    elif sensbase=='HIGH1':
        tradMode=True
        dbmval=-77
    elif sensbase=='HIGH2':
        tradMode=True
        dbmval=-82
    elif sensbase=='HIGH3':
        tradMode=True
        dbmval=-87
    if tradMode:
        if speed is not None and (speed.upper()=='2X' or speed.upper()=='X2') or (speed is None 
        and len(senssplit)>1 and ('2X' in senssplit[1] or 'X2' in senssplit[1])):
            return dbmval+2#x2 speed mode
        elif speed is None or speed.upper()=='1X' or speed.upper()=='X1' :
            return dbmval#x1 speed mode
        else:
            print('Invalid Speed')
            return -1
    #Rapid sensitivities do not have x1 or x2 speed
    elif sensbase=='RAPID1':
        dbmval=-52
    elif sensbase=='RAPID2':
        dbmval=-57
    elif sensbase=='RAPID3':
        dbmval=-62
    elif sensbase=='RAPID4':
        dbmval=-67
    elif sensbase=='RAPID5':
        dbmval=-72
    elif sensbase=='RAPID6':
        dbmval=-74
    else:#Invalid.  ret
        print('Invalid Sensitivity setting')
        return -1
    return dbmval
    
def sensitivityFromCode(code):
    """sensitivityFromCode:
    Returns the sensitivity name from a given code
    INPUTS:
    code (int or string): The code number (response from :sens:sens)
    OUTPUTS:
    The sensitivity name as a string"""
    return sensitivities[int(code)]

def codeFromSensitivity(sensitivity):
    """codeFromSensitivity:
    Returns the code from a given sensitivity name using sequential search:
    INPUTS:
    sensitivity (string): The sensitivity name
    RETURNS:
    The correesponding sensitivity code; -1 if no corresponding code"""
    for idx in range(len(sensitivities)):
        if sensitivities[idx]==sensitivity:
            return idx
    print('Invalid Sensitivity Setting')
    return -1

class AQ6380Controls:
    """class AQ6380Controls:
        A simple controls class for the AQ"""
    def __init__(self, address=None, port='10001', username='anonymous', password='aaa'):
        """initialize:
        INPUTS:
            address (str): The ip address of the OSA, default None
            port (str, default '10001'): The port of the OSA
            username (str, default 'anonymous'): The username for sign in
            password (str, default 'aaa'): The password for sign in
            Throws exception if address is of an invalid format
            """
        if address is not None:
            m = re.match(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', address.strip())
            if not m:
                print('Wrong IP format.')
                raise ValueError(f"IP address of {address} is invalid")
        self.address=address
        self.port=port
        self.resourceManager=pyvisa.ResourceManager()
        self.username=username
        self.password=password
        self.osa=None
        self.inSweep=False
        self.connected=False

    def setAddress(self, address):
        """setAddress:
        Sets the IP address of the OSA object
        INPUTS:
        address (str): The ip address of the OSA
        Throws exception if address is invalid."""
        m = re.match(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', address.strip())
        if not m:
            print('Wrong IP format.')
            raise ValueError(f"IP address of {address} is invalid")
        self.address=address
    def open(self):
        """open: Opens/connects to the OSA
        Throws exception if connection fails or address is not set"""
        #Connect to OSA via pyvisa resource manager
        if self.address is None:
            raise ValueError('No IP address given')#
        
        self.osa=self.resourceManager.open_resource(f'TCPIP::{self.address}::{self.port}::SOCKET', open_timeout=5000)
        self.connected=True
        self.osa.read_termination = '\n'
        self.osa.write_termination = '\n'
        a = self.query("open \""+self.username+"\"")    # send username & get strings
        print('OPENED: '+str(a))
        a = self.query(self.password)    # send password & get "ready" strings
        print(a)
        
    def query(self, cmd):
        """query: Sends a SCPI query to the OSA
        INPUTS:
        cmd (str): The command to send, should end in '?'
        RETURNS:
        The result of the query command, None if not connected"""
        if not self.connected:#Check for connection status
            print('OSA Not Connected')
            return None
        return self.osa.query(cmd)#Query command from OSA
    def write(self, cmd):
        """write: Sends a SCPI command to the OSA
        INPUTS:
        cmd (str): The command to send
        RETURNS:
        The result (length) of the write command, None if not connected"""
        if not self.connected:#Check for connection status
            print('OSA Not Connected')
            return None
        return self.osa.write(cmd)#Write command to OSA
    def sendSCPI(self, cmd):
        """sendScpi: Sends a SCPI command to the OSA
        Sends a query command if the command contains '?'
        Otherwise, sends a write command
        INPUTS:
        cmd (str): The command to send
        RETURNS:
        The result of the command if query command
        The length of the command if write command"""
        if '?' in cmd:#Query command format
            return self.query(cmd)
        else:#Write command format
            return self.write(cmd)
    def setCenter(self, center):
        """setCenter: Sets the center point of the OSA sweep
        INPUTS: 
        center (str or int): The center wavelength in nm
        RETURNS:
        The return of the osa write command (number of bytes sent)"""
        return self.write(f':sens:wav:cent {center}nm')#Set center value
    def setSpan(self, span):
        """setSpan: Sets the span of the OSA sweep
        INPUTS: 
        span (str or int): The span in nm
        RETURNS:
        The return of the osa write command (number of bytes sent)"""
        self.write(f':sens:wav:span {span}nm')#Set span value
    def setSensitivity(self, sens):
        """setSensitivity: Sets the sensitivity of the OSA
        INPUTS:
        sens (str or int): The sensitivity to set
        RETURNS:
        The result of the osa write command"""
        try:#Try to parse sensitivity as integer
            sensint=int(sens)
            return self.write(f':sens:sens {sensitivityFromCode(sensint)}')
        except Exception as e:#If not, try raw sensitivity name
            return self.write(f':sens:sens {sens}')
    def getSensitivity(self):
        """getSensitivity: Gets the current sensitivity of the OSA
        RETURNS:
        The current sensitivity as a sensitivity code.
        Use sensitivityFromCode to get sensitivity name."""
        return self.query(':sens:sens?')#Query the sensitivity value, return it as a sensitivity code string
    def setSweepSpeed(self, speed):
        """setSweepSpeed:
        Sets the sweep speed of the OSA
        INPUTS:
        speed (int or string): The sweep speed to set
                Valid values are "1x" "2x" 0 and 1
        RETURNS:
        The return of the write command"""
        try:#Check if speed is int
            speedint=int(speed)
            if speedint==0:#Parse and assign sweep speed
                sweepspeed='1x'
            elif speedint==1:
                sweepspeed='2x'
        except Exception as e:#Otherwise, try raw sweep speed name
            sweepspeed=speed
        finally:
            return self.write(f':sens:swe:spe {sweepspeed}')#Write the sweep speed to the OSA
    def getSweepSpeed(self):
        """getSweepSpeed: Gets the current sweep speed:
        Returns 0 for 1x, 1 for 2x"""
        return self.query(f':sens:swe:spe?')#Get and return sweep speed from OSA
    def setResolution(self, resolution):
        """setResolution: Sets the Resolution of the OSA in nm
        INPUTS:
        resolution (float or str): The resolution in nm
        OUTPUTS:
        The return of the write command"""
        if resolution not in resolutions:#Invalid resolution
            print(f'Resolution of {resolution} invalid')
            return None
        return self.write(f':sens:band {resolution}nm')#Set resolution on OSA
    def getResolution(self):
        """getResolution: Gets the current resolution
        RETURNS:
        The current resolution in nm (float)"""
        resstr=self.query(':sens:band?')#Get resolution in meters
        return float(resstr)*1e9#Return resolution in nm
    
    def singleSweep(self, center=None, span=None):
        """singleSweep: Performs a single sweep of the OSA
        INPUTS:
        center (str): The center in nm
        span (str): The span in nm
        RETURNS:
        True if sweep is a success, False if exception is thrown
        """
        if center is not None:
            self.setCenter(center)
        if span is not None:
            self.setSpan(span)
        self.write(':init:smode 1')#Single Sweep Mode
        self.write("*CLS")
        self.write(':init')#Start sweep
        #wait until sweep complete
        completeFlag=False
        try:
            while not completeFlag:
                queryval = self.query(":stat:oper:even?")#Is sweep complete>
                if queryval.strip()[-1] == "1":#Sweep is complete
                    completeFlag=True
        except Exception as e:
            print(f'Error: {e}')#Print exception
            return False
        else:
            return True
        
    def getPeakWavelength(self):
        """getPeakWavelength: Returns peak wavelength from previous sweep:
        RETURNS:
        The peak wavelength in nm (float)"""
        queryval= self.query(":calc:cat filp; :calc; :calc:data?")#Get peak data
        return float(queryval.split(',')[0].strip())*1e9#Return wavelength in nm

    def getPeakPower(self):
        """getPeakPower: Returns peak power from previous sweep
        RETURNS:
        The peak power in dBm (float)"""
        queryval= self.query(":calc:cat filp; :calc; :calc:data?")#Get peak data
        return float(queryval.split(',')[1].strip())#Return peak power
    def activateTrace(self, tracename):
        """activateTrace:
        Activates trace with name tracename
        INPUTS:
        tracename (str): The trace to activate
        RETURNS:
        The result from the activation command"""
        traceformatstr=':trac:act'
        if len(tracename)>0:
            traceformatstr +=' '+tracename
        return self.write(traceformatstr)#Set active trace
    def getActiveTrace(self):
        """getActiveTrace:
        Gets current active trace:
        RETURNS:
        The name of the active trace"""
        return self.query(':trac:act?')
    def getTraceVals(self):
        """getTraceVals:
        Gets the trace data from the OSA in ascii format and converts it to floating point
        RETURNS
        (xvals, yvals) where xvals is all wavelengths in nm
        and yvals is the corresponding amplitudes in dBm"""
        xstr=self.query(':trac:x? TRA')
        ystr=self.query(':trac:y? TRA')
        xsplit=xstr.split(',')#Split csv x axis
        ysplit=ystr.split(',')#Split csv y axis
        xvals=[round(float(x)*1e9, 4) for x in xsplit]
        yvals=[float(y) for y in ysplit]
        return (xvals, yvals)
    