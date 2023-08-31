#!bin/bash

sudo ln -sf $HOME/waspi/src/waspi/services/run_waspi.service /usr/lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable run_waspi.service
sudo systemctl start run_waspi.service
systemctl status run_waspi.service