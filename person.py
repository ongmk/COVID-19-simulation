import numpy as np

CONFIG = {
    "HEIGHT" : 100,
    "DT" : 1,
    "RADIUS" : 3.,
    "INFECTED_P" : 0.05,
    "SOCIAL_DISTANCING_FACTOR" : 0,
    "POPULATION" : 1000
}

# colors
COLOR_SCHEME = {
    "S" : "#34BF49",
    "I" : "#FF4C4C",
    "R" : "#0099E5",
    "D" : "#7B8D8E"
}

class Person:
    def __init__(self):
        # parameters
        self.set_status("S")
        self.radius = CONFIG["RADIUS"]
        self.infected_p = CONFIG["INFECTED_P"]
        self.social_dist_factor = CONFIG["SOCIAL_DISTANCING_FACTOR"]
        self.neighbours_pos=[]
        self.neighbours_status = []
        self.maxVel = 1

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

    def check_infection(self):
        if len(self.neighbours_status) != 0:
            infected_neighbour = np.sum(self.neighbours_status=="Infected")
            if np.random.rand() < infected_neighbour * self.infected_p:
                self.set_status("I")

    def update(self):
        dt = CONFIG["DT"]
        self.social_dist()
        self.vel += self.acc * dt
        if np.linalg.norm(self.vel) > self.maxVel:
            self.vel = self.maxVel * self.vel / np.linalg.norm(self.vel)
        self.pos += self.vel*dt
        self.check_infection()
        if self.pos[0] > CONFIG["HEIGHT"] or self.pos[0] < -CONFIG["HEIGHT"]:
            self.vel[0] = -self.vel[0]
        if self.pos[1] > CONFIG["HEIGHT"] or self.pos[1] < -CONFIG["HEIGHT"]:
            self.vel[1] = -self.vel[1]


class Community:
    def __init__(self,population= CONFIG["POPULATION"]):
        self.population = population
        self.people = [Person() for i in range(population)]
        [person.set_status("I") for person in self.people[:10]]

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
        d_count = np.sum(self.get_status() == "Dead")
        return [s_count, i_count, r_count, s_count]

    def update(self):
        poss = []
        colors = []
        positions = self.get_positions()
        people = self.get_people()
        status = self.get_status()
        index = np.arange(self.population)
        for i, pos, person in zip(index, positions, people):
            distances = np.linalg.norm(positions - person.pos, axis=1)
            neighbours_index = np.where(np.logical_and(distances < person.radius, index != i))[0]
            person.neighbours_pos = positions[neighbours_index]
            person.neighbours_status = status[neighbours_index]
            person.update()
            poss.append(person.pos)
            colors.append(person.color)
        return poss, colors, status, self.status_count()
