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

7. Install pdm - package manager [introduction to pdm](https://pdm.fming.dev/latest/)
```
curl -sSL https://pdm.fming.dev/install-pdm.py | python3 -
export PATH=/home/pi/.local/bin:$PATH
```

8. Install all dependencies 
```
pdn add arrow pyserial pydantic paho-mqtt
pip install .
```

9. Install and setup InfluxDB 

    1. Documentation InfluxDB Installation: [Click here for docs.](https://docs.influxdata.com/influxdb/v2.7/install/?t=Linux)
    2. Start influxDB instance on RPi. 
    3. Connect to influxDB via web broswer --> Web address *http://USERNAME_PI.local:8086*
    4. Setup influxDB --> chose a username, organisation name, bucket name
    5. Naviguate to "Load Data" -> "Telegraf". Select "+ Create Configuration". Chose the bucket and find the configuration file template "MQTT Consumer".
``` 
wget https://dl.influxdata.com/influxdb/releases/influxdb2-2.7.0-arm64.deb
sudo dpkg -i influxdb2-2.7.0-arm64.deb

sudo service influxdb start
```

10. Install telegraf - Get data from RPi into InfluxDB

    1. Documentation Telegraf Installation: [Click here for docs.](https://docs.influxdata.com/telegraf/v1.27/)
    2. Move the original telegraf configuration file and create a new telegraf conf file based on MQTT Consumer Template
    3. Start telegraf 
```
wget -q https://repos.influxdata.com/influxdata-archive_compat.key
echo '393e8779c89ac8d958f81f942f9ad7fb82a25e133faddaf92e15b16e6ac9ce4c influxdata-archive_compat.key' | sha256sum -c && cat influxdata-archive_compat.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg > /dev/null
echo 'deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian stable main' | sudo tee /etc/apt/sources.list.d/influxdata.list
sudo apt-get update && sudo apt-get install telegraf

sudo mv /etc/telegraf/telegraf.conf /etc/telegraf/telegraf-original.conf
sudo nano /etc/telegraf/telegraf.conf
sudo systemctl start telegraf.service
```

11. Install grafana 

    1. Documentation Grafana Installation: [Click here for docs.](https://grafana.com/grafana/download?platform=arm)
    2. Add grafana to systemd - start grafana service.
    3. Login into grafana at the address: http://localhost:3000 -> Default username and password: admin admin
    4. Setup Grafana -> Add Data to dashboard. Add DataSources -> Flux Query -> HTTP URL -> Basic Auth Details -> InfluxDB Details 

```
sudo apt-get install -y adduser libfontconfig1
wget https://dl.grafana.com/enterprise/release/grafana-enterprise_10.1.0_arm64.deb
sudo dpkg -i grafana-enterprise_10.1.0_arm64.deb

sudo /bin/systemctl daemon-reload
sudo /bin/systemctl enable grafana-server
sudo /bin/systemctl start grafana-server
```

12. Install waspi services
```
cd ~/waspi

bash waspi/scripts/start_waspi.sh
bash waspi/scripts/setup_heartbeat.sh
```
