from matplotlib import pyplot as plt
from matplotlib import animation
from person import Community

population = 1000
height = 1000

# colors
red = "#FF4C4C"
green = "#34BF49"
blue = "#0099E5"
grey = "7B8D8E"

with plt.style.context("dark_background"):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10),
                                   gridspec_kw={'height_ratios': [3, 1]})
ax1.set_aspect('equal')

community = Community(population)
scat = ax1.scatter([p.pos[0] for p in community.people],
                   [p.pos[1] for p in community.people],
                   c=[p.color for p in community.people],
                   s=20)
ax1.set_xlim(-height-100,height+100)
ax1.set_ylim(-height-100,height+100)

frames = [0]
s_data = [[p.status for p in community.people].count("Susceptible")]
i_data = [[p.status for p in community.people].count("Infected")]
graph = ax2.stackplot(frames,s_data,i_data,labels=["S","I"],
                      colors = [green,red])
ax2.set_ylim(0, population)
plots = [scat,graph]

def animate(frame):
    poss, colors = community.update()
    scat.set_offsets(poss)
    scat.set_color(colors)
    frames.append(frame)
    s_data.append([p.status for p in community.people].count("Susceptible"))
    i_data.append([p.status for p in community.people].count("Infected"))
    graph = ax2.stackplot(frames,s_data,i_data,labels=["S","I"],
                          colors = [green,red])
    ax2.set_xlim(0,frame)

    return plots


ani = animation.FuncAnimation(fig=fig, func=animate, frames=1000, interval=100, blit=False)
plt.show()