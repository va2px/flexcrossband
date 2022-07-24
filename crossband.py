''' Flex radio crossband repeater
    =============================
    Author:  Martin Berube  VA2PX
    email:   ve2nmb@gmail.com
    version: 0.1
    
    Perequisite:
    
    Flexradio 6xxx series transceiver with 2 SCU
    Python
    Frstack3 - For Rest API and "Level Meter Mute" feature
    SmartSDR DAX
    soundcard python module https://pypi.org/project/SoundCard/
    
    Summary:
    
    This softwaretransform your flexradio info a crossband repeater.  It will retransmit what it received on slace A and retransmit it on slice B and vice versa.  It utilises the "Level Meter Mute" of frstack3 software and send commands to te transciver via its REST API.  The programm uses DAX for audio reception and retransmition.  Crossband repeat in VHF/UHF is possible with transverters for these bands.
    
'''
import urllib.request
import soundcard as sc
import time

# Set up required paramaters in the transceiver
def setup():
    cmdA = urllib.request.urlopen('http://localhost:13522/api/Slice/A/DAX?PARAM=1')
    cmdB = urllib.request.urlopen('http://localhost:13522/api/Slice/B/DAX?PARAM=2')
    cmdFDX = urllib.request.urlopen('http://localhost:13522/api/Radio/FDX?PARAM=1')
    cmdDAX = urllib.request.urlopen('http://localhost:13522/api/Radio/DAX?PARAM=1')
    
    return

# This function listen on both slice.  When a slice get unmuted, its audio is transmitted over the other slice.    
def loop():
    # Soundcard parameters definition
    default_speaker = sc.get_speaker('DAX Audio TX')
    DAXrx1 = sc.get_microphone('Audio RX 1')
    DAXrx2 = sc.get_microphone('Audio RX 2')
    
    print(DAXrx1)
    print(DAXrx2)
    print(default_speaker)
    
    print('Crossband initiated - Listening')
    
    while True:
        muteAstat = urllib.request.urlopen('http://localhost:13522/api/Slice/A/MUTE')

        # Check mute state of slice A
        for line in muteAstat:
            line = line.decode().rstrip()

            if line == '\"OFF\"':
                # Set TX to slice B and enable MOX
                cmd = urllib.request.urlopen('http://localhost:13522/api/Slice/B/TX?param=1')
                cmd = urllib.request.urlopen('http://localhost:13522/api/Radio/MOX?PARAM=1')
                                
                print('Crossband transmit A -> B ') #Cosmetic
                
                # Start sound passover and keep sending sound while Mute is OFF.
                with DAXrx1.recorder(samplerate=48000) as mic, default_speaker.player(samplerate=48000) as sp:
                    # Check mute state of slice A
                    while line == '\"OFF\"':
                        sp.play(mic.record(numframes=None))
                        
                        muteAstat = urllib.request.urlopen('http://localhost:13522/api/Slice/A/MUTE')
                    
                        for line in muteAstat:
                            line = line.decode().rstrip()
                
                # Turn off MOX after 1 second wait.
                time.sleep(1)
                cmd = urllib.request.urlopen('http://localhost:13522/api/Radio/MOX?PARAM=0')
                
                print('Listening\r\n')   #Cosmetic

        muteBstat = urllib.request.urlopen('http://localhost:13522/api/Slice/B/MUTE')

        # Check mute state of slice B
        for line in muteBstat:
            line = line.decode().rstrip()
            
            if line == '\"OFF\"':
                # Set TX to slice B and enable MOX
                cmd = urllib.request.urlopen('http://localhost:13522/api/Slice/A/TX?param=1')
                cmd = urllib.request.urlopen('http://localhost:13522/api/Radio/MOX?PARAM=1')
                
                print('Crossband transmit B -> A') #Cosmetic
                
                # Start sound passover and keep sending sound while Mute is OFF.
                with DAXrx2.recorder(samplerate=48000) as mic, default_speaker.player(samplerate=48000) as sp:
                    # Check mute state of slice B
                    while line == '\"OFF\"':                    
                        sp.play(mic.record(numframes=None))
                        
                        muteBstat = urllib.request.urlopen('http://localhost:13522/api/Slice/B/MUTE')
                    
                        for line in muteBstat:
                            line = line.decode().rstrip()
                            
                # Turn off MOX after 1 second wait.
                time.sleep(1)                
                cmd = urllib.request.urlopen('http://localhost:13522/api/Radio/MOX?PARAM=0')
                
                print('Listening')   #Cosmetic 
    
if __name__ == '__main__':     # Program entrance
    setup()
    
    try:
        loop()

    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        # Clean up
        cmd = urllib.request.urlopen('http://localhost:13522/api/Radio/MOX?PARAM=0')
        cmdFDX = urllib.request.urlopen('http://localhost:13522/api/Radio/FDX?PARAM=0')
        cmdDAX = urllib.request.urlopen('http://localhost:13522/api/Radio/DAX?PARAM=0')
