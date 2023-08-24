## Setup BatDetect2 on RPi
#
1. Install raspbian OS - 64-bit lite on SDCard

2. Setup RPI with username and password

3. Check system update and upgrade
```
sudo apt update && sudo apt upgrade
````
3. Install dependencies
```
sudo apt install git 
#sudo apt install alsa-utils portaudio19-dev libsndfile1 libasound2-dev wget cmake
```
4. Install python3 and python3 libs
```
sudo apt install python3-dev python3-pip python3-venv
```

5. Move to home directory if not and clone the Acoupi GitHub repository (main) branch 
```
cd ~
git clone -b main --depth=1 https://github.com/audevuilli/waspi.git
```

6. Create .gitignore file
```
touch ~/.gitignore_global
git config --global core.excludesfile ~/.gitignore_global
nano ~/.gitignore_global
```

7. Install influxdb and grafana

    1. Documentation InfluxDB Installation: [Click here for docs.](https://docs.ainfluxdata.com/influxdb/v2.7/install/?t=Linux)
    2. Start influxDB instance on RPi.
    3. Connect to influxDB via web broswer --> Web address *http://USERNAME_PI:8086*

``` 
wget https://dl.influxdata.com/influxdb/releases/influxdb2-2.7.0-arm64.deb
sudo dpkg -i influxdb2-2.7.0-arm64.deb

sudo service influxdb start
```

8. Install dependencies with pip in acoupi folder
```
cd acoupi
pip install update -U pip
pip install -e .
pip install batdetect2
```

9. Install run_acoupi.service
```
cd ~/acoupi/
bash src/acoupi/scripts/batdetect2_setup_service.sh
bash src/acoupi/scripts/setup_heartbeat.sh
```

10. Setup cronjob for routine system cleaning.
```
crontab -e
0 17 * * * /bin/bash /home/pi/acoupi/src/acoupi/clean_system/recordings_folder.sh
0 0 * * 0 /bin/bash /home/pi/acoupi/src/acoupi/clean_system/clean_log.sh
0 0 1 * * /bin/bash /home/pi/acoupi/src/acoupi/clean_system/rename_acoupidb.sh
```

10. Test if batdetect2 main.py work. 

10. Start service to run acoupi-batdetect2
bash $HOME/acoupi/src/acoupi/scripts/setup_service.sh