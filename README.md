# bot7200
Twitter bots in Python

Running on Docker in Raspberry Pi

docker build -t frank-i .
docker run -d --restart always --name frank -v ~/bot7200/frank-tv/:/bots/ frank-i

docker build -t frank-fav-i .
docker run -d --restart always --name frank-fav frank-fav-i

frank-tv-x:
 docker build -t frank-x-image .
 docker run -d --restart always --name frank -v ~/bot7200/frank-tv/:/bots/ frank-x-image
 
