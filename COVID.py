from person import Community, COLOR_SCHEME, CONFIG
from matplotlib import pyplot as plt
from matplotlib import animation

with plt.style.context("dark_background"):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10),
                                   gridspec_kw={'height_ratios': [3, 1]})
ax1.set_aspect('equal')

community = Community()
scat = ax1.scatter([p.pos[0] for p in community.people],
                   [p.pos[1] for p in community.people],
                   c=[p.color for p in community.people],
                   s=20)
ax1.set_xlim(-CONFIG["HEIGHT"]-100,CONFIG["HEIGHT"]+100)
ax1.set_ylim(-CONFIG["HEIGHT"]-100,CONFIG["HEIGHT"]+100)

frames = [0]
status_count = community.status_count()
s_data = [status_count[0]]
i_data = [status_count[1]]
graph = ax2.stackplot(frames,s_data,i_data,labels=["S","I"],
                      colors = [COLOR_SCHEME["S"],COLOR_SCHEME["I"]])
ax2.set_ylim(0, CONFIG["POPULATION"])
plots = [scat,graph]

def animate(frame):
    poss, colors, status, status_count = community.update()
    scat.set_offsets(poss)
    scat.set_color(colors)
    frames.append(frame)
    s_data.append(status_count[0])
    i_data.append(status_count[1])
    graph = ax2.stackplot(frames,s_data,i_data,labels=["S","I"],
                          colors = [COLOR_SCHEME["S"],COLOR_SCHEME["I"]])
    ax2.set_xlim(0,frame)

    return plots


ani = animation.FuncAnimation(fig=fig, func=animate, frames=1000, interval=100, blit=False)
plt.show()