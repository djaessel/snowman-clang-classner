# This Python file uses the following encoding: utf-8

import time


class Stopwatch:
    def __init__(self):
        self.running = False
        self.startTime = 0
        self.endTime = 0
        pass


    def start(self):
        self.running = True
        self.startTime = time.time()
        self.endTime = 0


    def stop(self):
        self.running = False
        self.endTime = time.time() - self.startTime


    def printElapsed(self):
        if self.running:
            self.endTime = time.time() - self.startTime
        print("Time taken: ", str(int(self.endTime / 60)).rjust(2, "0") + ":" + str(int(self.endTime % 60)).rjust(2, "0"))
        print()

