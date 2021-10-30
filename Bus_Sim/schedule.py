import heapq

class Event:
    '''
    Events are entities with timestamps. Processing logic is abstracted
    out to the Simulation class. 
    '''

    def __init__(self, timestamp, entity) -> None:
        self.timestamp = timestamp
        self.entity  = entity

    def __lt__(self, other):
        return self.timestamp < other.timestamp


class Schedule:
    '''
    Implement an event schedule using a priority queue.
    '''
    
    def __init__(self):
        self.now = 0
        self.queue = []

    def add_event_at(self, timestamp, entity):
        heapq.heappush(self.queue, Event(timestamp, entity))

    def add_event_after(self, interval, entity):
        heapq.heappush(
            self.queue, 
            Event(self.now + interval, entity)
        )

    def get_next_event(self):
        next_event = heapq.heappop(self.queue)
        return next_event.timestamp, next_event.entity

    def next_event_time(self):
        # Min heaped so first entry is minimum of timestamp = earliest
        return self.queue[0].timestamp

    def print_events(self):
        for event in sorted(self.queue):
            print(f'   {event.timestamp}: {event.entity}')
