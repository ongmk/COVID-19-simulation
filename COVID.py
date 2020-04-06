from person import Community, COLOR_SCHEME, CONFIG
from matplotlib import pyplot as plt
from matplotlib import animation, gridspec

with plt.style.context("dark_background"):
    fig = plt.figure(figsize=(8,5))
    plt.suptitle("COVID-19 Simulation")
    gs = gridspec.GridSpec(2, 2, width_ratios=[3, 4],
                           wspace=0.3, hspace=0.3)
    ax1 = plt.subplot(gs[:,0])
    ax1.set_aspect('equal')
    ax2 = plt.subplot(gs[1])
    ax3 = plt.subplot(gs[3],sharex = ax2)

# Init Community
community = Community()
scat = ax1.scatter([p.pos[0] for p in community.people],
                   [p.pos[1] for p in community.people],
                   c=[p.color for p in community.people],
                   s=20)
ax1.set_xlim(-CONFIG["HEIGHT"]*1.1,CONFIG["HEIGHT"]*1.1)
ax1.set_ylim(-CONFIG["HEIGHT"]*1.1,CONFIG["HEIGHT"]*1.1)

# Init Graph
times = [0]
status_count = community.status_count()
s_data = [status_count[0]]
i_data = [status_count[1]]
r_data = [status_count[2]]
d_data = [status_count[3]]
stack = ax2.stackplot(times, i_data, s_data, r_data, d_data,labels=["I","S","R","D"],
                      colors = [COLOR_SCHEME["I"], COLOR_SCHEME["S"],
                                COLOR_SCHEME["R"], COLOR_SCHEME["D"]])
ax2.set_ylim(0, CONFIG["POPULATION"])
ax2.legend(prop={'size': 6})
ax2.set_ylabel("Population")
ax2.set_xlabel("Day")

# Init Daily plot
days = [0]
daily_data = [i_data[0]]
daily = ax3.bar(days,daily_data, color=COLOR_SCHEME["I"])
ax3.set_ylabel("Daily Confirmed Case")

pause = False
def onClick(event):
    global pause
    pause ^= True

def animate(frame):
    if not pause:
        # Update community
        poss, colors, status, status_count = community.update()
        scat.set_offsets(poss)
        scat.set_color(colors)

        # Update Stackplot
        times.append(community.time/CONFIG["TIME_IN_DAY"])
        s_data.append(status_count[0])
        i_data.append(status_count[1])
        r_data.append(status_count[2])
        d_data.append(status_count[3])
        stack = ax2.stackplot(times, i_data, s_data, r_data, d_data, labels=["I","S","R","D"],
                              colors = [COLOR_SCHEME["I"],COLOR_SCHEME["S"],
                                        COLOR_SCHEME["R"],COLOR_SCHEME["D"]])
        current_time = times[-1]
        if frame != 0:
            ax2.set_xlim(0, current_time)
            ax3.set_xlim(0,current_time)

        # Update daily plot
        if int(current_time)-current_time == 0.0:
            days.append(current_time)
            daily_data.append(s_data[-int(CONFIG["TIME_IN_DAY"]/CONFIG["DT"])-1]-s_data[-1])
            daily = ax3.bar(days,daily_data, color=COLOR_SCHEME["I"])
            stack = [scat] + stack + daily.patches

            return stack
        stack.append(scat)
        return stack


fig.canvas.mpl_connect('button_press_event', onClick)
ani = animation.FuncAnimation(fig=fig, func=animate, frames=1000, interval=1, blit=False)
plt.show()