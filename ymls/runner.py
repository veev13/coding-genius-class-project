import time
import os
import sys

if sys.argv[1] == '0':
    print("RUN_FILE is '0'!")
    exit(0)
while not os.path.isfile(sys.argv[1]):
    time.sleep(5)
print("RUN!")
os.execlp('python', sys.argv[1])
