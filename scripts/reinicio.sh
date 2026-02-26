docker-compose down
docker-compose up --build -d
docker-compose stop frontend
docker-compose run --service-ports frontend


