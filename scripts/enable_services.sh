sudo systemctl enable --now postgresql.service
sudo systemctl enable --now /home/sentisounds/CS4800-SentiSounds/services/sentisoundsAPI.service
sudo apt install nginx
sudo cp ~/CS4800-SentiSounds/services/nginx/nginx.conf /etc/nginx/nginx.conf
sudo systemctl enable --now nginx.service
