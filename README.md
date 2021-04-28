# bot7200
Twitter bot in Python that requests a tweet to Atlas DB throught maslabook.com and tweet it every 7200 seconds (2 hours)

Running on Docker in Raspberry Pi


docker run -d --restart always --name frank -v ~/bot7200/frank-tv/:/bots/:ro frank-i