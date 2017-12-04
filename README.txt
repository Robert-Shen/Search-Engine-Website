============= Instruction =============
To deploy a new AWS EC2 instance and launch web server:
1. Under root directory, open ‘config.py’ and modify ‘AWS_Access_Key_Id’ and ‘AWS_Secret_Access_Key’
2. Delete any existing 'login.pem' from root directory
3. Run ‘python awsDeployer.py’

To terminate the instance:
1.Under root directory, run ‘python awsTerminator.py’
2. This will default to terminate the instance you created when deployment, you can change to terminate another instance by providing instance id

============= Live Web Server ============
Public DNS and IP and istance id refers to config.py



============= How to run Backend ============
To demonstrate the functionality of crawler and pagerank algorithm:
1. Run server.py
2. All data will be store to persistent storage

To demonstrate the persistent storage
1. Run run_backend_test.py
2. In the terminal will display all of crawled links with their scores
   Note: only links that send out link will be scored, for other links who received link, a zero score will be assigned

============= Benchmark Setup ============
1. Create and initialize two AWS instances, use on as web app server, the other one as tester
2. Login to server instance by:
ssh -i KeyPair.pem ubuntu@52.5.119.86
3. Launch web app from server instance by:
sudo python FrontEnd.py
5. Start benchmarking from local machine:
ab -n 460 -c 440 http://52.5.119.86/?keywords=helloworld+foo+bar
ab -n 500 -c 50 http://52.5.119.86/?keywords=helloworld+foo+bar

============= Benchmark Result ============
SHENZIPENG-MacBook-Pro:326lab SZP$ ab -n 200 -c 15 http://52.5.119.86/?keywords=helloworld+foo+bar
This is ApacheBench, Version 2.3 <$Revision: 1757674 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 52.5.119.86 (be patient)
Completed 100 requests
Completed 200 requests
Finished 200 requests


Server Software:        WSGIServer/0.1
Server Hostname:        52.5.119.86
Server Port:            80

Document Path:          /?keywords=helloworld+foo+bar
Document Length:        1213 bytes

Concurrency Level:      15
Time taken for tests:   1.334 seconds
Complete requests:      200
Failed requests:        0
Total transferred:      308600 bytes
HTML transferred:       242600 bytes
Requests per second:    149.92 [#/sec] (mean)
Time per request:       100.054 [ms] (mean)
Time per request:       6.670 [ms] (mean, across all concurrent requests)
Transfer rate:          225.90 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:       29   36  22.5     35     351
Processing:    40   61  24.9     58     210
Waiting:       39   60  24.9     57     208
Total:         73   97  34.2     92     405

Percentage of the requests served within a certain time (ms)
  50%     92
  66%     93
  75%     94
  80%     95
  90%     97
  95%    113
  98%    233
  99%    247
 100%    405 (longest request)

============= Benchmark Result ============
The result of lab3 is lower than lab2, which handled 460 requests at 400 concurrencies.
The decrease in the performance can be affected by the connection to the persistent database.
Since every query of the keywords will establish a connection to the db, thus the workload is increased for lab3 and resulted in the decrease of performance.
