sudo pip3 install -r requirements.txt
sudo cp contec.ini /etc/nginx/apps/
sudo cp agents_contec.conf /etc/supervisor/conf.d/
sudo cp agents_contec_nginx.conf /etc/nginx/sites-enabled/
sudo supervisorctl update
sudo systemctl restart nginx
sudo certbot --nginx -d contec.ai.medsenger.ru
touch config.py
