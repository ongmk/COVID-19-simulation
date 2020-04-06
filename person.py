import numpy as np

CONFIG = {
    "HEIGHT" : 50,
    "DT" : 1,
    "SOCIAL_RADIUS" : 4.5,
    "INFECT_RADIUS" : 3.,
    "SOCIAL_DISTANCING_FACTOR" : 1, # 0 or 1
    "POPULATION" : 200,
    "INFECTED_P": 0.5,
    "RECOVERED_P" : 0.005,
    "DEATH_P" : 0.002,
    "DEAD_DAY" : 3,
    "TIME_IN_DAY" : 10,
    "CAPACITY" : 100
}


# colors
COLOR_SCHEME = {
    "S" : "#0099E5",
    "I" : "#FF4C4C",
    "R" : "#34BF49",
    "D" : "#333333"
}

class Person:
    def __init__(self):
        # parameters
        self.set_status("S")
        self.social_radius = CONFIG["SOCIAL_RADIUS"]
        self.infect_radius = CONFIG["INFECT_RADIUS"]
        self.infected_p = CONFIG["INFECTED_P"]
        self.social_dist_factor = CONFIG["SOCIAL_DISTANCING_FACTOR"]
        self.social_neighbours_pos=[]
        self.infect_neighbours_status = []
        self.maxVel = 1
        self.infected_time = 0
        self.recovered_p = CONFIG["RECOVERED_P"]
        self.death_p = CONFIG["DEATH_P"]
        self.dead_time = CONFIG["DEAD_DAY"]*CONFIG["TIME_IN_DAY"]

        # position parameters
        self.pos = np.array((np.random.rand(2)-0.5)*2*CONFIG["HEIGHT"])
        self.vel = (np.random.rand(2)+0.3)*2
        for i in range(2):
            if np.random.rand() < 0.5:
                self.vel[i] = -self.vel[i]
        self.acc = np.zeros(2)

    def social_dist(self):
        repulsion_force = np.zeros(2)
        if self.social_dist_factor > 0:
            min_dist = np.inf
            for pos in self.neighbours_pos:
                displacement = pos - self.pos
                distance = np.linalg.norm(displacement)
                if 0 < distance < min_dist:
                    min_dist = distance
                if distance > 0:
                    repulsion_force -= self.social_dist_factor * displacement / (distance**3)
        self.acc = repulsion_force

    def set_status(self, status):
        assert status in ["S","I","R","D"]
        self.status = {"S":"Susceptible",
                       "I":"Infected",
                       "R":"Recovered",
                       "D":"Dead"}[status]
        self.color = COLOR_SCHEME[status]
        if status == "I":
            self.infected_time = 1
        else:
            self.infected_time = 0

    def check_status_change(self, dt):
        if self.status == "Susceptible":
            if len(self.neighbours_status) != 0:
                infected_neighbour = np.sum(self.neighbours_status=="Infected")
                if np.random.rand() < infected_neighbour * self.infected_p:
                    self.set_status("I")
        elif self.status == "Infected":
            if np.random.rand() < self.recovered_p:
                self.set_status("R")
            else:
                if self.infected_time > self.dead_time:
                    if np.random.rand() < self.death_p:
                        self.set_status("D")
                    else:
                        self.infected_time += dt
                else:
                    self.infected_time += dt

    def update(self):
        dt = CONFIG["DT"]
        self.social_dist()
        self.vel += self.acc * dt
        if np.linalg.norm(self.vel) > self.maxVel:
            self.vel = self.maxVel * self.vel / np.linalg.norm(self.vel)
        self.pos += self.vel*dt
        self.check_status_change(dt)
        if self.pos[0] > CONFIG["HEIGHT"]:
            self.vel[0] = -np.abs(self.vel[0])
        elif self.pos[0] < -CONFIG["HEIGHT"]:
            self.vel[0] = np.abs(self.vel[0])
        if self.pos[1] > CONFIG["HEIGHT"]:
            self.vel[1] = -np.abs(self.vel[1])
        elif self.pos[1] < -CONFIG["HEIGHT"]:
            self.vel[1] = np.abs(self.vel[1])


class Community:
    def __init__(self,population= CONFIG["POPULATION"]):
        self.initial_population = population
        self.population = population
        self.people = [Person() for i in range(population)]
        self.time = 0
        self.capacity = CONFIG["CAPACITY"]
        [person.set_status("I") for person in self.people[:max(int(0.01*population),1)]]

    def get_positions(self):
        return np.array([person.pos for person in self.people])

    def get_status(self):
        return np.array([person.status for person in self.people])

    def get_people(self):
        return self.people

    def status_count(self):
        s_count = np.sum(self.get_status() == "Susceptible")
        i_count = np.sum(self.get_status() == "Infected")
        r_count = np.sum(self.get_status() == "Recovered")
        d_count = self.initial_population-s_count-i_count-r_count
        return [s_count, i_count, r_count, d_count]

    def remove_dead(self):
        dead_index = list(np.where(self.get_status()=="Dead")[0])
        for index in sorted(dead_index, reverse=True):
            del self.people[index]
            self.population -= 1

    def update(self):
        self.time += CONFIG["DT"]
        poss = []
        colors = []
        self.remove_dead()
        status = self.get_status()
        status_count = self.status_count()
        positions = self.get_positions()
        people = self.get_people()
        index = np.arange(self.population)
        for i, pos, person in zip(index, positions, people):
            distances = np.linalg.norm(positions - person.pos, axis=1)
            if status_count[1] >= self.capacity:
                person.death_p = CONFIG["DEATH_P"]*4
            else:
                person.death_p = CONFIG["DEATH_P"]
            social_neighbours_index = np.where(np.logical_and(distances < person.social_radius, index != i))[0]
            infect_neighbours_index = np.where(np.logical_and(distances < person.infect_radius, index != i))[0]
            person.neighbours_pos = positions[social_neighbours_index]
            person.neighbours_status = status[infect_neighbours_index]
            person.update()
            poss.append(person.pos)
            colors.append(person.color)
        return poss, colors, status, status_count
