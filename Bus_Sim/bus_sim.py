
import numpy as np
import matplotlib.pyplot as plt
from functools import reduce

from entities import BusStop, Bus, Stats
from schedule import Schedule
from utils import transpose_to_plot, mins_to_hours
import scipy.stats as sts


class Simulation:
    def __init__(self, total_buses = 5, final_time = 24*60, lambda_ = 1, extended = False, pass_extended = False) -> None:
        # params
        self.total_buses = total_buses
        self.total_stops = 15
        self.final_time  = final_time 

        self.extended = extended
        self.pass_extended = pass_extended

        # SIM variables:
        self.served_passengers  = []
        self.max_queue_length = 0

        # Initialize simulation
        self.schedule  = Schedule()

        if self.extended:
            self.lambda_ = 1.2 + np.cos(np.pi*(self.schedule.now - 7)/6)
        else: 
            self.lambda_ = lambda_

        # Instantiate BusStops and load onto event schedule
        self.bus_stops = [BusStop(i + 1, lambda_ = self.lambda_) for i in range(self.total_stops)]
        for stop in self.bus_stops:
            self.schedule.add_event_at(0, stop)

        # Create a bus at each starting index. Bus_n <= BusStop_n
        self.buses = [Bus(location = i + 1, last_stop = self.total_stops) 
                      for i 
                      in range(self.total_buses)]
        for bus in self.buses:
            self.schedule.add_event_at(0, bus)

        # Initialize Stats data collector
        self.stats = Stats()
        self.schedule.add_event_at(0, self.stats)
        self.bus_times = []
        self.arrival_times = []
        self.annoyed = []
        self.steady_mean = 0

    def run(self):
        while self.schedule.now < self.final_time: 
            # take the next event
            curr_time, entity = self.schedule.get_next_event()
            # update schedule to current time
            self.schedule.now = curr_time

            if isinstance(entity, BusStop):

                if self.extended:
                    # Update arrival rate
                    hour = mins_to_hours(curr_time)
                    lambda_prime = 1.2 + np.cos(np.pi*(hour - 7)/6)
                    entity.lambda_ = lambda_prime

                if self.pass_extended:
                    # Second extension: annoyed passengers leave
                    a_pass = entity.get_annoyed_and_leave(curr_time)
                    if a_pass:
                        self.annoyed.append((curr_time,a_pass))

                # Let a customer arrive
                queue_length = entity.customer_arrival(self.schedule, curr_time, self.total_stops)
                
                if entity.stop_index == 1:
                    self.arrival_times.append(curr_time)                

                # Check the maximum queue length
                if self.max_queue_length < queue_length:
                    self.max_queue_length = queue_length

            elif isinstance(entity, Bus):
                # check where bus is
                current_stop = self.bus_stops[entity.location - 1]

                if entity._capacity == len(entity.passengers):
                    entity.full = True
                else:
                    entity.full = False

                # For sanity plot
                if entity._name == 1:
                    self.bus_times.append((curr_time, entity.location, entity.full))

                disembark_time, departed_customers = entity.unload_passengers(current_stop)
                loading_time = entity.load_passengers(curr_time, current_stop)
                delay = loading_time + disembark_time

                # Update sim variable
                self.served_passengers.append((curr_time, departed_customers, entity._name, entity.location))

                # Move Bus to next stop, with loading/unloading delay is complete
                entity.move_to_next_stop(self.schedule, delay)

            elif isinstance(entity, Stats):
                entity.sample(self.schedule, curr_time, self)

    def cum_plot(self):
        # An overview/sanity check plot
        for bus in range(1, self.total_buses + 1):
            bus_data = list(filter(lambda d: d[2] == bus, self.served_passengers))
            plot_data = list(zip(*bus_data))

            plot_data[1] = [len(plot_data[1][i]) for i in range(len(plot_data[1]))]

            x = plot_data[0]
            y = np.cumsum(plot_data[1])

            plt.plot(x, y, label = f'Bus {bus} Cumulative Departures')
            plt.legend()

    def wait_times(self):
        data = list(zip(*self.served_passengers))

        # compute wait times
        wait_times = [[p.departure_time - p.arrival_time for p in el] for el in data[1]]
        # flatten array
        wait_times = reduce(lambda x,y: x + y, wait_times)

        return np.mean(wait_times)


    def sanity_plot(self):
        data = transpose_to_plot(self.served_passengers)

        fig = plt.figure(figsize=(25,10))
        fig.suptitle(f"Sanity Plots for Simulation with {self.total_buses} Bus over {self.final_time} minutes")

        gs = fig.add_gridspec(3,2, wspace= 0.4, hspace = 0.2)

        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[1, 1])
        ax4 = fig.add_subplot(gs[2, 0])
        ax5 = fig.add_subplot(gs[2, 1])

        # Plot interrarival times
        mean_inter = np.mean([i[0] for i in np.diff(self.bus_times, axis = 0)])
        ax2.hist([i[0] for i in np.diff(self.bus_times, axis = 0)], bins = 30)
        ax2.axvline(mean_inter , color = "red", linewidth = 1, \
                        linestyle = '--', label = f"Mean transit time = {round(mean_inter)} mins")
        ax2.set_xlabel("Interarrival Times for Bus 1")
        ax2.set_ylabel("Frequency")
        ax2.legend()
        
        # Compute, flatten and plot wait times
        wait_times = [[p.departure_time - p.arrival_time for p in el] for el in data[1]]
        wait_times = reduce(lambda x,y: x + y, wait_times)
        expected_val = np.mean(wait_times)

        ax3.hist(wait_times, bins = 50)
        ax3.axvline( expected_val, color = "red", linewidth = 1, \
                        linestyle = '--', label = f"Mean waiting time = {round(expected_val)} mins")
        ax3.set_xlabel(f"Passenger Waiting Times (mins) across {self.total_buses} Buses")
        ax3.legend(loc = "lower right")


        # Compute interarrivals at Stop 1 :: ~Exponential if event schedule works
        inter_arrivals = np.diff(self.arrival_times)
        ax4.hist(sts.expon.rvs(scale = 1, size = len(inter_arrivals)),
                    alpha = 0.5, label = "Theoretical Distribution")
        ax4.hist(inter_arrivals, 
                    alpha = 0.5, label = f"Empirical Distribution")
        ax4.axvline(np.mean(inter_arrivals), color = "red", linestyle = "--", 
                       label = f"Empirical $\lambda  = {round(np.mean(inter_arrivals), 2)}$")
        ax4.legend(loc = "upper right")
        ax4.set_xlabel("BusStop 1 Interarrival Times")

        time_data = transpose_to_plot(self.stats.n_passengers)
    
        t = time_data[0]
        y = [np.mean(time_data[1][i]) for i in range(len(time_data[1]))]

        # average last 10 measurements
        self.steady_mean = np.mean(y[-10:-1])

        ax5.axhline(130, label = "Max capacity = 130", color = "red", linestyle = "--")
        ax5.plot(t,y)
        ax5.scatter(t,y)
        ax5.set_xlabel("Time since Midnight (mins)")
        ax5.set_ylabel("Avg. #Passengers in Bus")
        ax5.legend()

        # Plot initial events
        plot_data = transpose_to_plot(self.bus_times)
        # Sample times but truncate to first two hours
        bus_times = plot_data[0][:35]
        stop_arrivals = self.arrival_times[:150]

        # Color "red" if bus is full or not
        bus_cols = ["Red" if obs else "Blue" for obs in plot_data[2]][:35]
        stop_cols = ["Blue" for obs in stop_arrivals]
        cols = [bus_cols, stop_cols]


        events = [bus_times, stop_arrivals]
        ax1.eventplot(events, linelengths= 0.3, colors = cols)
        ax1.set_yticks([0,1])
        ax1.set_yticklabels(['Bus 1', 'Passenger Arrivals \n at Stop 1'])
        ax1.set_xlabel("Event Time since Midnight (mins)")


        return sts.kstest(inter_arrivals, sts.expon.cdf), wait_times, y

    def max_queue_plot(self):
        plot_data = transpose_to_plot(self.stats.max_queue)

        plt.plot(plot_data[0], plot_data[1])
        plt.xlabel("Time since Midnight (mins)")
        plt.ylabel("Longest queue length")
        plt.title("Maximum Queue Length across 15 Stops")

class BatchRunner:
    def __init__(self, total_buses = 5, run_count = 3) -> None:
        self.total_buses = total_buses
        self.run_count = run_count
        self.sim_data  = None
        self.plot_data = lambda: transpose_to_plot(self.sim_data.items())

    def batch_run(self):
        buses = range(1, self.total_buses + 1)
        sim_data = {bus: {"avg_wait": 0, "max_queue":0, "avg_passengers": 0} for bus in buses}

        for n_bus in buses:

            mean_wait_times = []
            max_queues = []
            avg_passengers = []

            for sim_run in range(self.run_count):
                this_sim = Simulation(total_buses=n_bus, extended= True, pass_extended= True)

                this_sim.run()

                mean = this_sim.wait_times()
                mean_wait_times.append(mean)

                max_queue = this_sim.max_queue_length
                max_queues.append(max_queue)

                avg_pass = this_sim.steady_mean
                avg_passengers.append(avg_pass)


            m = np.mean(mean_wait_times)
            t = sts.sem(mean_wait_times)

            sim_data[n_bus]["avg_wait"] = (m, 1.96*t)

            m_max = np.mean(max_queues)
            t_max = sts.sem(max_queues)

            sim_data[n_bus]["max_queue"] = (m_max, 1.96*t_max)

            m_pass = np.mean(avg_passengers)
            t_pass = sts.sem(avg_passengers)

            sim_data[n_bus]["avg_passengers"] = (m_pass, 1.96*t_pass)
        
        self.sim_data = sim_data

        return self.sim_data

    def wait_times_plot(self):
        if self.sim_data is not None:
            plot_data = self.plot_data()

            x = plot_data[0]

            y = [i["avg_wait"][0] for i in plot_data[1]]
            err = [i["avg_wait"][1] for i in plot_data[1]]

            plt.plot(x,y, color = "gray")
            plt.errorbar(x,y, err, fmt= '.k')
            plt.xlabel("Number of Buses")
            plt.ylabel("Mean Waiting Time (minutes)")
            plt.show()
        else:
            print("Run the simulation")


    def max_queue_plot(self):
        plot_data = self.plot_data()

        x = plot_data[0]

        y = [i["max_queue"][0] for i in plot_data[1]]
        err = [i["max_queue"][1] for i in plot_data[1]]

        plt.plot(x,y, color = "gray")
        plt.errorbar(x,y, err, fmt= '.k')
        plt.xlabel("Number of Buses")
        plt.ylabel("Max Queue Length (number of waiting passengers)")

    def mean_passengers_plot(self):
        # mean passengers at end of the simulation
        plot_data = self.plot_data()

        t = plot_data[0]

        y = [i["avg_passengers"][0] for i in plot_data[1]]
        err = [i["avg_passengers"][1] for i in plot_data[1]]

        plt.plot(t,y, color = "gray")
        plt.errorbar(t,y, err, fmt= '.k')
        plt.xlabel("Number of Buses")
        plt.ylabel("Avg #Passengers in Buses in Steady State")



