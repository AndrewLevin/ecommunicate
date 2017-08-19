sudo python -u server.py 2>&1 | tee server_log.dat >& /dev/null &
sudo python -u server_http.py 2>&1 | tee server_http_log.dat >& /dev/null &
