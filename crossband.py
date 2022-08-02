''' Crossband repeater software for Flex radio
    ==========================================
    Author:  Martin Berube  VA2PX
    email:   ve2nmb@gmail.com
    version: 0.3
    
    Syntax:  python crossband.py [frstack_address]
    
    Perequisite:
    
    Flexradio 6xxx series transceiver with 2 SCU
    Python
    Frstack3 - For Rest API and "Level Meter Mute" feature
    SmartSDR DAX
    soundcard python module https://pypi.org/project/SoundCard/
    
    Summary:
    
    This software transform your flexradio info a crossband repeater.  It will retransmit what it received on slace A and retransmit it on slice B and vice versa.  It utilises the "Level Meter Mute" of frstack3 software and send commands to te transciver via its REST API.  The programm uses DAX for audio reception and retransmition.  Crossband repeat in VHF/UHF is possible with transverters for these bands.
    
'''
import urllib.request
import soundcard as sc
import time
import json
import sys

# Set up required paramaters in the transceiver
def setup(argv):
    try:
        if argv[1]:
            frstackloc = argv[1]
    except:
        frstackloc = 'localhost'
        
    #FRStack URLs definitions    
    daxAto1 = 'http://'+frstackloc+':13522/api/Slice/A/DAX?PARAM=1'
    daxBto2 = 'http://'+frstackloc+':13522/api/Slice/B/DAX?PARAM=2'
    FDXto1 = 'http://'+frstackloc+':13522/api/Radio/FDX?PARAM=1'
    DAXto1 = 'http://'+frstackloc+':13522/api/Radio/DAX?PARAM=1'
        
    cmdA = urllib.request.urlopen(daxAto1)
    cmdB = urllib.request.urlopen(daxBto2)
    cmdFDX = urllib.request.urlopen(FDXto1)
    cmdDAX = urllib.request.urlopen(DAXto1)
    
    return(frstackloc)

# This function listen on both slice.  When a slice get unmuted, its audio is transmitted over the other slice.    
def loop(frstackloc,MOXto0):
    # Soundcard parameters definition
    default_speaker = sc.get_speaker('DAX Audio TX')
    DAXrx1 = sc.get_microphone('Audio RX 1')
    DAXrx2 = sc.get_microphone('Audio RX 2')
    
    #FRStack URLs definitions
    MOXto1 = 'http://'+frstackloc+':13522/api/Radio/MOX?PARAM=1'
    TxA = 'http://'+frstackloc+':13522/api/Slice/A/TX?param=1'
    TxB = 'http://'+frstackloc+':13522/api/Slice/B/TX?param=1'
    MuteA = 'http://'+frstackloc+':13522/api/Slice/A/MUTE'
    MuteB = 'http://'+frstackloc+':13522/api/Slice/B/MUTE'
    
    print(DAXrx1)
    print(DAXrx2)
    print(default_speaker)
    
    print('Crossband initiated - Listening')
    
    while True:
        muteAstat = urllib.request.urlopen(MuteA)
        line = json.loads(muteAstat.read().decode())

        # Check mute state of slice A
        if line == 'OFF':
            # Set TX to slice B and enable MOX
            cmd = urllib.request.urlopen(TxB)
            cmd = urllib.request.urlopen(MOXto1)
                                
            print('Crossband transmit A -> B ') #Cosmetic
                
            # Start sound passover and keep sending sound while Mute is OFF.
            with DAXrx1.recorder(samplerate=48000) as mic, default_speaker.player(samplerate=48000) as sp:
                # Check mute state of slice A
                while line == 'OFF':
                    sp.play(mic.record(numframes=None))
                        
                    muteAstat = urllib.request.urlopen(MuteA)
                    line = json.loads(muteAstat.read().decode())
                
                # Turn off MOX after 1 second wait.
                time.sleep(1)
                cmd = urllib.request.urlopen(MOXto0)
                
                print('Listening\r\n')   #Cosmetic

        muteBstat = urllib.request.urlopen(MuteB)
        line = json.loads(muteBstat.read().decode())

        # Check mute state of slice B
        if line == 'OFF':
            # Set TX to slice B and enable MOX
            cmd = urllib.request.urlopen(TxA)
            cmd = urllib.request.urlopen(MOXto1)
                
            print('Crossband transmit B -> A') #Cosmetic
                
            # Start sound passover and keep sending sound while Mute is OFF.
            with DAXrx2.recorder(samplerate=48000) as mic, default_speaker.player(samplerate=48000) as sp:
                # Check mute state of slice B
                while line == 'OFF':                    
                    sp.play(mic.record(numframes=None))
                        
                    muteBstat = urllib.request.urlopen(MuteB)
                    line = json.loads(muteBstat.read().decode())
                            
                # Turn off MOX after 1 second wait.
                time.sleep(1)                
                cmd = urllib.request.urlopen(MOXto0)
                
                print('Listening')   #Cosmetic 
    
if __name__ == '__main__':     # Program entrance
    frstackloc = setup(sys.argv)
    
    #FRStack URLs definitions
    MOXto0 = 'http://'+frstackloc+':13522/api/Radio/MOX?PARAM=0'
    FDXto0 = 'http://'+frstackloc+':13522/api/Radio/FDX?PARAM=0'
    DAXto0 = 'http://'+frstackloc+':13522/api/Radio/DAX?PARAM=0'

    try:
        loop(frstackloc,MOXto0)

    except KeyboardInterrupt:  # Press ctrl-c to end the program.
        # Clean up
        cmd = urllib.request.urlopen(MOXto0)
        cmdFDX = urllib.request.urlopen(FDXto0)
        cmdDAX = urllib.request.urlopen(DAXto0)
