from person import Community, COLOR_SCHEME, CONFIG
from matplotlib import pyplot as plt
from matplotlib import animation, gridspec
from matplotlib.patches import Patch

font = {'fontfamily':'serif','weight':'bold'}

with plt.style.context("dark_background"):
    fig = plt.figure(figsize=(8,5))
    plt.suptitle("COVID-19 Simulation",**font)
    gs = gridspec.GridSpec(4, 2, width_ratios=[3, 4],
                           wspace=0.3, hspace=0.3)
    ax1 = plt.subplot(gs[:3,0])
    ax1.set_aspect('equal')
    ax2 = plt.subplot(gs[:2,1])
    ax3 = plt.subplot(gs[2:,1],sharex = ax2)
    ax4 = plt.subplot(gs[3:, 0])

# Init Community
community = Community()
scat = ax1.scatter([],[],s=10)

# Init Graph
times = [0]
status_count = community.status_count()
s_data = [status_count[0]]
i_data = [status_count[1]]
r_data = [status_count[2]]
d_data = [status_count[3]]
stack = ax2.stackplot([],[],[],[])
capacity_line = ax2.hlines(y=CONFIG["CAPACITY"], xmin=0, xmax=1000, colors="r", linestyle='--', lw=2)

# Init Daily plot
days = [0]
daily_data = [i_data[0]]
daily = ax3.bar([],[], color=COLOR_SCHEME["I"])

def init():
    # init community
    ax1.set_xlim(-CONFIG["HEIGHT"] * 1.1, CONFIG["HEIGHT"] * 1.1)
    ax1.set_ylim(-CONFIG["HEIGHT"] * 1.1, CONFIG["HEIGHT"] * 1.1)
    scat.set_offsets([])

    # init graph
    ax2.set_ylim(0, CONFIG["POPULATION"])
    ax2.set_ylabel("Population",**font)
    ax2.set_xlabel("Day",**font)
    ax2.tick_params(right=True)
    stack = ax2.stackplot([], [], [], [], [])

    # init daily plot
    ax3.set_ylabel("Daily Case",**font)
    ax3.tick_params(right=True)
    daily = ax3.bar([], [], color=COLOR_SCHEME["I"])
    stack = stack+[scat]+daily.patches
    return stack

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
        times.append(community.time / CONFIG["TIME_IN_DAY"])
        s_data.append(status_count[0])
        i_data.append(status_count[1])
        r_data.append(status_count[2])
        d_data.append(status_count[3])
        stack = ax2.stackplot(times, i_data, s_data, r_data, d_data,
                              colors=[COLOR_SCHEME["I"], COLOR_SCHEME["S"],
                                      COLOR_SCHEME["R"], COLOR_SCHEME["D"]])
        legend_elements = [Patch(facecolor=COLOR_SCHEME["I"], edgecolor="w", label=f'I: {status_count[1]}'),
                           Patch(facecolor=COLOR_SCHEME["S"], edgecolor="w", label=f'S: {status_count[0]}'),
                           Patch(facecolor=COLOR_SCHEME["R"], edgecolor="w", label=f'R: {status_count[2]}'),
                           Patch(facecolor=COLOR_SCHEME["D"], edgecolor="w", label=f'D: {status_count[3]}')]
        legend = ax2.legend(handles=legend_elements, prop={'size': 6,'weight':"bold"}, loc=2,frameon=False)
        plt.setp(legend.get_texts(), color='w')
        current_time = times[-1]
        if frame != 0:
            ax2.set_xlim(0, current_time)

        # update daily plot
        if int(current_time) - current_time == 0.0:
            days.append(current_time)
            daily_data.append(d_data[-int(CONFIG["TIME_IN_DAY"] / CONFIG["DT"]) - 1] - d_data[-1])
            daily = ax3.bar(days, daily_data, color=COLOR_SCHEME["I"])
            stack = stack+[scat,capacity_line,legend]+daily.patches
            return stack

        stack = stack+[scat,capacity_line,legend]
        return stack

fig.canvas.mpl_connect('button_press_event', onClick)
ani = animation.FuncAnimation(fig=fig, func=animate, frames=100000000, interval=1, init_func=init, blit=True)
plt.show()