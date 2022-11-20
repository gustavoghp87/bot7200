# bot7200
Twitter bots in Python

Running on Docker in Raspberry Pi

################################################################################

docker run --rm -d -p 4444:4444 -p 5900:5900 -p 7900:7900 --shm-size 2g --name firefox seleniarm/standalone-firefox:latest

docker stop maslabook && docker rm maslabook && docker rmi maslabook-i && docker build -t maslabook-i /home/ubuntu/bot7200/maslabook/ && docker run -d --restart always --name maslabook maslabook-i

################################################################################

docker build -t frank-i .
docker run -d --restart always --name frank -v ~/bot7200/frank-tv/:/bots/ frank-i

################################################################################

docker build -t frank-fav-i .
docker run -d --restart always --name frank-fav frank-fav-i

################################################################################

docker stop frank-x && docker rm frank-x && docker rmi frank-x-image
docker build -t frank-x-image /home/ubuntu/bot7200/frank-tv-x
docker run -d --restart always --name frank-x -v ~/bot7200/frank-tv-x/:/bots/ frank-x-image

################################################################################

docker stop frank-z && docker rm frank-z && docker rmi frank-z-image && docker build -t frank-z-image /home/ubuntu/bot7200/frank-tv-z && docker run -d --restart always --name frank-z -v ~/bot7200/frank-tv-z/:/bots/ frank-z-image
