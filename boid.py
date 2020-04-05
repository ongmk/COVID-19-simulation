import numpy as np
class Person:
    def __init__(self):
        self.pos = np.array((np.random.rand(2)-0.5)*320)
        self.vel = (np.random.rand(2)+0.5)*4
        for i in range(2):
            if np.random.rand() < 0.5:
                self.vel[i] = -self.vel[i]
        self.acc = np.zeros(2)
        self.maxForce = 0.05
        self.maxSpeed = 10

    def steering(self, persons):
        radius = 60
        vels = []
        poss = []
        inv_dis = []
        force = np.zeros(2)
        for other in persons:
            if (np.linalg.norm(self.pos - other.pos) < radius) and (other != self):
                vels.append(other.vel)
                poss.append(other.pos)
                inv_dis.append((self.pos - other.pos)/ np.linalg.norm(self.pos - other.pos))
        if len(vels) > 0:

            # alignment
            align_steering = np.mean(vels, axis=0)
            if np.linalg.norm(align_steering)!= 0:
                align_steering = self.maxSpeed * align_steering / np.linalg.norm(align_steering)
            align_steering -= self.vel

            # cohesion
            cohesion_steering = np.mean(poss, axis=0)
            cohesion_steering -= self.pos
            if np.linalg.norm(cohesion_steering) != 0:
                cohesion_steering = self.maxSpeed * cohesion_steering / np.linalg.norm(cohesion_steering)
            cohesion_steering -= self.vel

            # seperation
            seperation_steering = np.mean(inv_dis, axis=0)
            if np.linalg.norm(seperation_steering) != 0:
                seperation_steering = self.maxSpeed * seperation_steering / np.linalg.norm(seperation_steering)
            seperation_steering -= self.vel

            force = align_steering + cohesion_steering + seperation_steering

            if np.linalg.norm(force) > self.maxForce:
                force = self.maxForce * force / np.linalg.norm(force)
        return force

    def flock(self, persons):
        force = self.steering(persons)
        self.acc = force

    def update(self):
        self.pos += self.vel
        if self.pos[0] > 320:
            self.pos[0] = -320
        elif self.pos[0] < -320:
            self.pos[0] = 320
        if self.pos[1] > 320:
            self.pos[1] = -320
        elif self.pos[1] < -320:
            self.pos[1] = 320
        self.vel += self.acc