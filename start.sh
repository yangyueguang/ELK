read -p "Please input IP address:" newip
oldip=$(cat docker-compose.yml | grep -Eo '([0-9]{1,3}\.){3}[0-9]{1,3}')
sudo sed -i 's/'${oldip}'/'${newip}'/' docker-compose.yml
# 如果在mac上则 sudo sed -i "" 's/'${oldip}'/'${newip}'/' docker-compose.yml
docker-compose up -d
sleep 10
docker exec gitlab-runner bash -c 'chmod 777 /home/gitlab-runner'