import threading

def printit(some_str: str, num=0):
    if num != 0:
        threading.Timer(5.0, printit, [some_str, num-1]).start()
        print(some_str)

printit("Bob", 2)