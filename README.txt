============= Live Web Server ============
Public DNS (IPv4):
ec2-52-5-119-86.compute-1.amazonaws.com

IPv4 Public IP:
52.5.119.86

============= Enabled Google API ============
Google login APIs

============= Benchmark Setup ============
1. Create and initialize two AWS instances, use on as web app server, the other one as tester
2. Login to server instance by:
ssh -i KeyPair.pem ubuntu@52.5.119.86
3. Login to tester instance by:
ssh -i KeyPair.pem ubuntu@34.197.54.29
4. Launch web app from server instance by:
sudo python FrontEnd.py
5. Start benchmarking from tester instance:
ab -n 460 -c 440 http://52.5.119.86/?keywords=helloworld+foo+bar
