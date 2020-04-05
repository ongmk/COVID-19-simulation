from matplotlib import pyplot as plt
from matplotlib import animation
from boid import Person

N = 60
fig, ax = plt.subplots()
ax = plt.axes(xlim=[-320,320],ylim=[-320,320])
ax.set_facecolor("black")

flock = [Person() for i in range(N)]

scat = plt.scatter([p.pos[0] for p in flock],
                   [p.pos[1] for p in flock],
                   c="w",
                   s=12)

def update(frame):
    poss = []
    for p in flock:
        p.flock(flock)
        p.update()
        poss.append(p.pos)
    scat.set_offsets(poss)
    return scat


ani = animation.FuncAnimation(fig=fig, func=update, frames=1000, interval=1, blit=False)
plt.show()