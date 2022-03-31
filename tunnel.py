from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Value
from multiprocessing import current_process
import time, random
NORTH = 0
SOUTH = 1
NCARS = 5


class Monitor():
    
    def __init__(self):
        self.mutex = Lock()
        self.Ncars = Value('i', 0)
        self.Scars = Value('i', 0)
        self.Ncars_waiting = Value('i', 0) 
        self.Scars_waiting = Value('i', 0)
        self.no_cars_goingN = Condition(self.mutex)
        self.no_cars_goingS = Condition(self.mutex)
    
    def no_cars_north(self):
        return self.Ncars.value == 0 and self.Ncars_waiting.value == 0
    
    def no_cars_south(self):
        return self.Scars.value == 0 and self.Scars_waiting.value == 0
    
    def wants_enter_north(self):
        self.mutex.acquire()
        self.Ncars_waiting.value += 1
        self.no_cars_goingS.wait_for(self.no_cars_south)
        self.Ncars_waiting.value -= 1
        self.Ncars.value += 1
        self.mutex.release()
    
    def leaves_tunnel_north(self):
        self.mutex.acquire()
        self.Ncars.value -= 1
        if self.Ncars.value == 0:
            self.no_cars_goingN.notify_all()
        self.mutex.release()
    
    def wants_enter_south(self):
        self.mutex.acquire()
        self.Scars_waiting.value += 1
        self.no_cars_goingN.wait_for(self.no_cars_north)
        self.Scars_waiting.value -= 1
        self.Scars.value += 1
        self.mutex.release()
        
    def leaves_tunnel_south(self):
        self.mutex.acquire()
        self.Scars.value -= 1
        if self.Scars.value == 0:
            self.no_cars_goingS.notify_all()
        self.mutex.release()
    
def delay(n=3):
    time.sleep(random.random()*n)
    
def northcar(cid,monitor):
    delay()
    print(f"car {cid} heading north wants to enter")
    monitor.wants_enter_north()
    print(f"car {cid} heading north enters the tunnel")
    delay()
    print(f"car {cid} heading north out of the tunnel")
    monitor.leaves_tunnel_north()

def southcar(cid,monitor):
    delay()
    print(f"car {cid} heading south wants to enter")
    monitor.wants_enter_south()
    print(f"car {cid} heading south enters the tunnel")
    delay()
    monitor.leaves_tunnel_south()
    print(f"car {cid} heading south out of the tunnel")

def main():
    monitor = Monitor()
    cars=[]
    for cid in range(NCARS):
        direction = NORTH if random.randint(0,1)==0 else SOUTH
        if direction == NORTH:
            p = Process(target=northcar, args=(cid,monitor))
        else:
            p = Process(target=southcar, args=(cid,monitor))
        p.start()
        cars.append(p)
    for p in cars:
        p.join()
if __name__ == '__main__':
    main()
    