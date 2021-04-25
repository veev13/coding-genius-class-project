import time
import os
import sys

print("PROGRAM START")
if sys.argv[1] == '0':
    print("RUN_FILE is '0'!")
    exit(0)
print(f'{sys.argv[1]} FIND START')
with open("logs.txt", 'w') as f:
    f.write(f"FIND START {sys.argv[1]}")
while not os.path.isfile(sys.argv[1]):
    time.sleep(5)
print("RUN!")
os.system(f'python {sys.argv[1]}')

