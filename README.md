Crossband repeater software for Flex radio
==========================================
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
    
This software transform your flexradio info a crossband repeater.  It will retransmit what it received on slace A and retransmit it on slice B and vice versa.  It utilises the "Level Meter Mute" of frstack3 software and send commands to te transciver via its REST API.  The programm uses DAX for audio reception and retransmition.  Crossband repeat in VHF/UHF is possible with transverters for these bands.
