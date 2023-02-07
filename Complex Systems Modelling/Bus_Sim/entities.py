import random
import scipy.stats as sts
import heapq
from utils import transpose_to_plot
import numpy as np

class BusStop:
    def __init__(self, stop_index, lambda_ = 1) -> None:
        # customers waiting for bus
        self.stop_queue = []
        self.stop_index  = stop_index
        self.lambda_ = lambda_
        self.arrival_distribution = lambda: sts.expon.rvs(scale = 1/self.lambda_)

    def customer_arrival(self, schedule, curr_time, n_stops = 5):

        # First come first served : either heap or sort before entering
        heapq.heappush(self.stop_queue, Passenger(arrival_time = curr_time, source = self.stop_index, total_stops = n_stops))
        #schedule next customer arrival
        schedule.add_event_after(self.arrival_distribution(), self)

        return len(self.stop_queue)

    def get_annoyed_and_leave(self, curr_time): 
        # Check from the 21st passenger onwards
        annoyed_passengers = []

        if len(self.stop_queue) > 20:
            sorted_passengers = sorted(self.stop_queue)
            possibly_annoyed = sorted_passengers[21:]

            for passenger in possibly_annoyed:
                if passenger.annoyed(curr_time):
                    annoyed_passengers.append((curr_time - passenger.arrival_time))
                    self.stop_queue.remove(passenger)

            if len(annoyed_passengers):
                #print(annoyed_passengers)
                return annoyed_passengers 

class Passenger:
    def __init__(self, arrival_time, source, total_stops = 5) -> None:
        self.arrival_time = arrival_time
        self.source_stop = source
        # Loop around, while mainting 1-start indexing for stops
        self.destination_stop = (self.source_stop + random.randint(0,6))%total_stops + 1

        self.departure_time = None

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time


    def print_attrs(self):
        print(f'source is {self.source_stop} dest is {self.destination_stop}')

    def annoyed(self, curr_time):
        wait_time = curr_time - self.arrival_time
        return wait_time > 10




class Bus:
    def __init__(self, location, last_stop) -> None:
        # Index of the stop the bus is currently at
        self.location = location

        self._name = location
        self._capacity = 130
        self._transit_time  = lambda: sts.truncnorm.rvs(a = 0, b = 10, loc = 2, scale = 0.5)
        self._boarding_time = lambda n: sts.truncnorm.rvs(a = 0,b = 10, loc = 0.05*n, scale = 0.01*(n**0.5))
        self._disembark_time = lambda n: sts.truncnorm.rvs(a = 0,b = 10, loc = 0.03*n, scale = 0.01*(n**0.5))
        self._last_stop = last_stop
        self.full = False

        # Passengers currently in bus
        self.passengers  = []

    def move_to_next_stop(self, schedule, delay):
        # Update position, loop around if need be
        if self.location < self._last_stop:
            self.location += 1
        else: 
            self.location = 1

        # Schedule next stop
        travel_time = self._transit_time()
        schedule.add_event_after(travel_time + delay, self)

    def load_passengers(self, curr_time, bus_stop):
        max_to_board  = self._capacity - len(self.passengers)

        n_to_board = min(len(bus_stop.stop_queue), max_to_board)
        time_to_load = self._boarding_time(n_to_board)

        # Load passengers on a first come, first served basis
        for p in range(n_to_board):
            # Exit the stop
            boarding_passenger = heapq.heappop(bus_stop.stop_queue)
            # Stamp the Passenger with departure time
            boarding_passenger.departure_time = curr_time

            # Add to bus
            self.passengers.append(boarding_passenger)

        return time_to_load

    def unload_passengers(self, bus_stop):
        # Identify passengers who need to get off
        departing_passengers = list(filter(lambda p: p.destination_stop == bus_stop.stop_index, self.passengers))
        unload_time = self._disembark_time(len(departing_passengers))

        for passenger in departing_passengers:
            self.passengers.remove(passenger)

        # Report unload time, departed Passengers for data collecting
        return unload_time, departing_passengers


class Stats:
    def __init__(self, interval = 10) -> None:
        self.n_passengers = []
        self.max_queue = []
        self.interval = interval 

    def sample(self, schedule, curr_time, simulation):
        
        self.n_passengers.append((curr_time, [len(i.passengers) for i in simulation.buses]))

        self.max_queue.append((curr_time, simulation.max_queue_length))

        time_data = transpose_to_plot(self.n_passengers)
        y = [np.mean(time_data[1][i]) for i in range(len(time_data[1]))]

        # steady state is avg of last 10 measurements
        simulation.steady_mean = np.mean(y[-10:])

        # Schedule next Stats sampling
        schedule.add_event_after(self.interval, self)

