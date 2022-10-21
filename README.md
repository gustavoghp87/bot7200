# bot7200
Twitter bots in Python

Running on Docker in Raspberry Pi


docker build -t frank-i .
docker run -d --restart always --name frank -v ~/bot7200/frank-tv/:/bots/ frank-i


docker build -t frank-fav-i .
docker run -d --restart always --name frank-fav frank-fav-i


docker stop frank-x && docker rm frank-x && docker rmi frank-x-image
docker build -t frank-x-image /home/ubuntu/bot7200/frank-tv-x
docker run -d --restart always --name frank-x -v ~/bot7200/frank-tv-x/:/bots/ frank-x-image

docker stop frank-x && docker rm frank-x && docker rmi frank-x-image && docker build -t frank-x-image /home/ubuntu/bot7200/frank-tv-x && docker run -d --restart always --name frank-x -v ~/bot7200/frank-tv-x/:/bots/ frank-x-image
