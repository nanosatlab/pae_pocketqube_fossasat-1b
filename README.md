# PocketQube following FOSSASAT-1B design for PAE
This respository aims at presenting the documentation necessary to manufacture a FossaSat-1B pocketqube. It is intended to be used by the Projecte Avançat d'Enginyeria (PAE) of the Universitat Politècnica de Catalunya (UPC). This repository has been created due to the lack of information and documentation of the original repository.

## Folder tree structure
The project is structure as follows:

- ground_station: this folder contains all the code to set up the LoRa ground station.
  - lora: this folder contains the code to be flashed in the [Heltec WiFi LoRa 32 (v2)](https://heltec.org/project/wifi-lora-32/). More information of its library can be found in its [repository](https://github.com/HelTecAutomation/Heltec_ESP32).
  - python: this folder contains the code to interact with the Heltec, and thus to parse raw data to packet format. Additionally, it forwards these packets to the server that is hosting the web.
- website: this folder contains all the code to set up the web page that notifies the reception of the packets.
  - backend: this folder contains all the code to interact with the ground station and store the received packets.
  - frontend: this folder contains all the code to plot in a web page the received packets.
- satellite: this folder contains the code of the satellite, briefly adapted. It has been forked from its [repository](https://github.com/FOSSASystems/FOSSASAT-1B) an partially adapted to current scenario.
- doc: this folder contains the information of the FOSSASat-1B. It is directly forked from its [repository](https://github.com/FOSSASystems/FOSSASAT-1B).


## Steps to execute the ground station
Follow these steps to set up the ground station, which will help to verify your own implementation. Those steps are presented for GNU-Linux computer. If you are using Windows, the Flasing process should be equal, and the python execution should also be close. However, do not use Windows, it is not healthy.

### Flash the LoRa device
Open the file /ground_station/lora/ground_station/ground_station.ino with the Arduino IDE. In the "Tools" panel, select the "Board" "Heltec ESP32 Arduino/WiFi LoRa 32(V2)". If this board is not available, you must install the Arduino libraries of Heltec. Follow the instructions in this [repository](https://github.com/HelTecAutomation/Heltec_ESP32) to perform that.

Connect the Heltec module with a USB wire to the computer. If the module is powered on, select the corresponding port at the "Port" field of the "Tools" panel. The port should be in the family "/dev/ttyUSBX" where X correspond to a number.

Once the port is configured and the module connected to the computer, flash the ground_station.ino code using "Upload" button. Once the flashing process is done, your LoRa device is ready, and you should see some log in the Heltec screen.

### Start the thread
Enter in folder /ground_station/python and execute the python script "ground_station.py": python3 ground_station.py; It is important to execute it with python3, because it has been implemented for this version. If you do not have the Heltec module connected to the computer you will see an error like this:

``` [ERROR] Serial port /dev/ttyUSB0: [Errno 2] could not open port /dev/ttyUSB0: [Errno 2] No such file or directory: '/dev/ttyUSB0' ```

You must connect the Heltec module and check the port name. However, if after connecting the module to the computer, the error persist. You must modify the port name in the /ground_station/python/Configuration.py file and put the corresponding one.

The thread is correctly executed when the following log is printed in the screen: 

``` Serial port /dev/ttyUSB0 opened with: {500000} ```

Let's see how to check the correct reception of the packets.

### Read the log
The reception of the packets are firstly indicated in the Heltec screen. There, the received packets are tagged with a counter and their lenght (in bytes). Additionally, the received RSSI is printed to also know how close to the communications limits it is. 

Moreover, all the packets that are received are forwarded to the ground_station.py; thus to perform the test, you must have connected the Heltec module, and running the ground_station.py script (see previous section). This script stores all the recieved packets in different files:

- rx_lora_log_file_YYYY_MM_DD_HH_mm_ss: contains all the received packets and which have correctly parsed. Where YYYY corresponds to the creation year, MM the mont, DD the day, etc.
- log_YYYY_MM_DD_HH_mm_ss: contains additional log with all the received raw data from the LoRa module.

All those files are generated per execution, which means that if you stop the ground_station.py thread and starts again a new set of files are created with the new date. To read those files at real time, you can use the following command in a new terminal:

``` tail -f log_YYYY_MM_DD_HH_mm_ss ```

### Close the ground station thread
While the ground_station.py script is trying to connect to a backend, it will stay stuck and you will not be able to close it (with a SIGNQUIT). Therefore, you must pause the thread and then manually kill it. Here a picture as example:

![Pause and Kill](/images/pause-and-kill.png)

To pause a thread, you have to click Ctrl+Z.



