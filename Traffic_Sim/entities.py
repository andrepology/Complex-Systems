class Lane:
    # a 1D Nagel-Schreckenberg simulation using Cars
    def __init__(self, env, road_length = 20, car_density = 0.7, max_speed = 5, prob_slow = 0.2) -> None:
        self.road_length = road_length

        self.direction = 'EW'
        
        # TODO: arrival_rate based on empirical prior
        self.env = env
        self.time = lambda: env.curr_time

        self.representation = np.full(self.road_length, -1, dtype=int)
        self.previous_states = [self.representation]

        # Init cars or road based on Lane params // speeed limits vary by lane
        self.car_density = car_density
        self.max_speed = max_speed
        self.prob_slow = prob_slow

        self.cars = []
        car_idxs = np.random.choice(
                range(self.road_length),
                size=int(round(car_density * self.road_length)),
                replace=False)

        for i in car_idxs:
            velocity_i = np.random.randint(0 , self.max_speed + 1)
            new_car = Car(position = i,
                        velocity = velocity_i,
                        max_speed = self.max_speed, 
                        prob_slow = self.prob_slow)
            heapq.heappush(self.cars, new_car)

    def set_representation(self):
        # get positions of cars, set index
        new_representation = np.full(self.road_length, -1, dtype=int)

        for car in self.cars:
            car_idx = car.position
            car_vel = car.velocity

            new_representation[car_idx] = car_vel

        self.previous_states.append(new_representation)
        self.representation = new_representation

        return

        
    def display(self):
        #self.set_representation()
        print(''.join('.' if x == -1 else str(x) for x in self.representation))

    def update(self):
        # calculate next_pos
        cars_ = sorted(self.cars)

        for i, car in enumerate(sorted(self.cars)):
            next_car  = cars_[(i + 1) % len(self.cars)]

            dist = (next_car.position - car.position) % self.road_length
            car.calc_next_position(dist)

        # set next_pos
        for car in self.cars:
            car.update_position(self.road_length)

        self.set_representation()

    def show_lane(self):

        prev = self.previous_states

        fig, ax  = plt.subplots(1,1, figsize= (3,3))

        for i in range(len(prev)):
            # Filter out empty cells
            y_cars = np.arange(0, len(prev[i]))[prev[i] != -1]
            
            t = [i]*len(y_cars)
            t_points = list(zip([0]*len(y_cars), y_cars))

            c = prev[i][prev[i] != -1]

            # Make colorbar a func of speed
            a = ax.scatter(y_cars, t, c = c, alpha = 0.6, marker = 'o', cmap='bone_r')

        ax.set_yticks(range(len(prev)))
        ax.set_axis_off()
        ax.set_title(f'Space-Time Diagram after {ev.curr_time} Steps')


        #plt.colorbar(a)
        plt.gca().invert_yaxis()
        return fig, ax
          
class Environment:
    # Variables of sim and current time
    def __init__(self, road_length, car_density, max_speed, prob_slow) -> None:
        self.curr_time = 0
        self.lanes = [Lane(self, road_length, car_density, max_speed, prob_slow)]

    def update(self):
        for lane in self.lanes:
            # update 
            lane.update()
            # increment time
        self.curr_time += 1

class Car:
    def __init__(self, position, velocity, max_speed, prob_slow) -> None:
        self.position = position
        self.velocity = velocity

        self.next_velocity = velocity
        self.max_speed = max_speed
        self.prob_slow = prob_slow

    def __lt__(self, other):
        return self.position < other.position

    def __repr__(self) -> str:
        return f'Car at {self.position} with {self.velocity} cells/step'   

    def calc_next_position(self, dist):
        # Acceleration
        if self.velocity < self.max_speed:
            self.next_velocity = self.velocity + 1

        # Slow down
        if self.next_velocity >= dist:
            self.next_velocity = dist - 1

        # Random Transition Probability
        if self.next_velocity > 0:
            gamble = np.random.random() < self.prob_slow
            if gamble:
                self.next_velocity -= 1
    
    def update_position(self, max_length):
        self.velocity = self.next_velocity

        self.position += self.velocity
        self.position %= max_length
