import numpy as np

height = 1000

# colors
red = "#FF4C4C"
green = "#34BF49"
blue = "#0099E5"
grey = "7B8D8E"

class Person:
    def __init__(self):
        # parameters
        self.status = 'Susceptible'
        self.radius = 20.
        self.infected_p = 0.05
        self.social_dist_factor = 0
        self.n_repulsion_points = 20
        self.neighbours_pos=[]
        self.neighbours_status = []
        self.maxVel = 1

        # position parameters
        self.pos = np.array((np.random.rand(2)-0.5)*2*height)
        self.vel = (np.random.rand(2)+0.3)*12
        for i in range(2):
            if np.random.rand() < 0.5:
                self.vel[i] = -self.vel[i]
        self.acc = np.zeros(2)

        # plotting parameters
        self.color = green

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

    def set_status(self):
        if len(self.neighbours_status) != 0:
            infected_neighbour = np.sum(self.neighbours_status=="Infected")
            if np.random.rand() < infected_neighbour * self.infected_p:
                self.status = "Infected"
                self.color = red
        return self.color

    def update(self):
        dt = 10
        self.social_dist()
        self.vel += self.acc * dt
        if np.linalg.norm(self.vel) > self.maxVel:
            self.vel = self.maxVel * self.vel / np.linalg.norm(self.vel)
        self.pos += self.vel*dt
        self.color = self.set_status()
        if self.pos[0] > height or self.pos[0] < -height:
            self.vel[0] = -self.vel[0]
        if self.pos[1] > height or self.pos[1] < -height:
            self.vel[1] = -self.vel[1]


class Community:
    def __init__(self,n):
        self.population = n
        self.people = [Person() for i in range(n)]
        self.people[0].status = "Infected"
        self.people[0].color = red

    def get_positions(self):
        return np.array([person.pos for person in self.people])

    def get_status(self):
        return np.array([person.status for person in self.people])

    def get_people(self):
        return self.people

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
        return poss, colors
