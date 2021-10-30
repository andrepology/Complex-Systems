import numpy as np

class Lane:
    # a 1D Nagel-Schreckenberg simulation using Cars
    def __init__(self, env, road_length = 10, car_density = 0.3, max_speed = 5, prob_slow = 0.2) -> None:
        self.road_length = road_length
        self.direction = 'EW'
        
        # TODO: arrival_rate based on some
        self.env = env
        self.time = lambda: env.curr_time

        self.representation = np.full(self.road_length, -1, dtype=int)

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
            self.cars.append(new_car)

    def set_representation(self):
        # get positions of cars, set index
        for car in self.cars:
            car_idx = car.position
            car_vel = car.velocity

            self.representation[car_idx] = car_vel

    def display(self):
        self.set_representation()
        print(''.join('.' if x == -1 else str(x) for x in self.representation))
        return 

    def update(self):
        # calculate next_pos
        # set next_pos
        return



class Environment:
    # Variables of sim and current time
    def __init__(self) -> None:

        self.curr_time = 0
        self.lanes = [Lane(self)]

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
        
        self.max_speed = max_speed
        self.prob_slow = prob_slow


        