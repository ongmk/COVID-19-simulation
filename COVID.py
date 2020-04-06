from person import Community, COLOR_SCHEME, CONFIG
from matplotlib import pyplot as plt
from matplotlib import animation, gridspec

font = {'fontfamily':'serif','weight':'bold'}

# for animating axis or titles
def _blit_draw(self, artists, bg_cache):
    # Handles blitted drawing, which renders only the artists given instead
    # of the entire figure.
    updated_ax = []
    for a in artists:
        # If we haven't cached the background for this axes object, do
        # so now. This might not always be reliable, but it's an attempt
        # to automate the process.
        if a.axes not in bg_cache:
            # bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox)
            # change here
            bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.figure.bbox)
        a.axes.draw_artist(a)
        updated_ax.append(a.axes)

    # After rendering all the needed artists, blit each axes individually.
    for ax in set(updated_ax):
        # and here
        # ax.figure.canvas.blit(ax.bbox)
        ax.figure.canvas.blit(ax.figure.bbox)


# MONKEY PATCH!!
animation.Animation._blit_draw = _blit_draw

with plt.style.context("dark_background"):
    fig = plt.figure(figsize=(8,5))
    plt.suptitle("COVID-19 Simulation",**font)
    gs = gridspec.GridSpec(4, 2, width_ratios=[3, 4],
                           wspace=0.3, hspace=0.5)
    ax1 = plt.subplot(gs[:3,0])
    ax1.set_aspect('equal')
    ax2 = plt.subplot(gs[:2,1])
    ax3 = plt.subplot(gs[2:,1],sharex = ax2)
    ax4 = plt.subplot(gs[3:, 0], frameon=False)

    ax2.xaxis.set_animated(True)
    ax3.xaxis.set_animated(True)
    ax3.yaxis.set_animated(True)

# Setup Community
community = Community()
scat = ax1.scatter([],[],s=10)

# Setup Graph
times = [0]
status_count = community.status_count()
s_data = [status_count[0]]
i_data = [status_count[1]]
r_data = [status_count[2]]
d_data = [status_count[3]]
stack = ax2.stackplot([],[],[],[])
capacity_line = ax2.hlines(y=CONFIG["CAPACITY"], xmin=0, xmax=1000, colors="r", linestyle='--', lw=1.5)
line_label = ax2.text(0,CONFIG["CAPACITY"]*1.1,"  Capacity", fontsize=10,color="r")

# Setup Daily plot
days = [0]
daily_data = [i_data[0]]
daily = ax3.bar([],[], color=COLOR_SCHEME["I"])

# Setup Counter
s_counter = ax4.text(0.33, 0.6, "", fontweight="bold", fontsize=16, horizontalalignment='left',color=COLOR_SCHEME["S"])
i_counter = ax4.text(0.83, 0.6, "", fontweight="bold", fontsize=16, horizontalalignment='left',color=COLOR_SCHEME["I"])
r_counter = ax4.text(0.33, 0.0, "", fontweight="bold", fontsize=16, horizontalalignment='left',color=COLOR_SCHEME["R"])
d_counter = ax4.text(0.83, 0.0, "", fontweight="bold", fontsize=16, horizontalalignment='left',color='grey')
s_label = ax4.text(0.3, 0.6, "Susceptible", fontsize=8, horizontalalignment='right',color=COLOR_SCHEME["S"])
i_label = ax4.text(0.8, 0.6, "Infected", fontsize=8, horizontalalignment='right',color=COLOR_SCHEME["I"])
r_label = ax4.text(0.3, 0.0, "Recovered", fontsize=8, horizontalalignment='right',color=COLOR_SCHEME["R"])
d_label = ax4.text(0.8, 0.0, "Dead", fontsize=8, horizontalalignment='right',color="grey")

def init():
    # init community
    ax1.set_xlim(-CONFIG["HEIGHT"] * 1.1, CONFIG["HEIGHT"] * 1.1)
    ax1.set_ylim(-CONFIG["HEIGHT"] * 1.1, CONFIG["HEIGHT"] * 1.1)
    scat.set_offsets([])

    # init graph
    ax2.set_ylim(0, CONFIG["POPULATION"])
    ax2.set_ylabel("Population",**font)
    ax2.tick_params(right=True)
    stack = ax2.stackplot([], [], [], [], [])

    # init daily plot
    ax3.set_ylabel("Daily Case",**font)
    ax3.tick_params(right=True)
    ax3.set_xlabel("Day",**font)
    daily = ax3.bar([], [], color=COLOR_SCHEME["I"])

    # init counter
    ax4.tick_params(left=False, bottom=False,labelleft=False, labelbottom=False)
    ax4.set_ylim()
    s_counter.set_text("")
    i_counter.set_text("")
    r_counter.set_text("")
    d_counter.set_text("")

    stack = stack+[scat,s_counter,i_counter,r_counter,d_counter]+daily.patches
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

        current_time = times[-1]
        if frame != 0:
            ax2.set_xlim(0, current_time)
            ax3.set_xlim(0, current_time)

        # update daily plot
        if int(current_time) - current_time == 0.0:
            days.append(current_time)
            daily_data.append(d_data[-int(CONFIG["TIME_IN_DAY"] / CONFIG["DT"]) - 1] - d_data[-1])

        # Update counter
        s_counter.set_text("{}".format(status_count[0]))
        r_counter.set_text("{}".format(status_count[2]))
        i_counter.set_text("{}".format(status_count[1]))
        d_counter.set_text("{}".format(status_count[3]))

    stack = ax2.stackplot(times, i_data, s_data, r_data, d_data,colors=[COLOR_SCHEME["I"], COLOR_SCHEME["S"],
                                                                        COLOR_SCHEME["R"], COLOR_SCHEME["D"]])
    daily = ax3.bar(days, daily_data, color=COLOR_SCHEME["I"])
    stack = stack+[ax2.xaxis,ax3.xaxis,ax3.yaxis,
                   scat,capacity_line,line_label,
                   s_counter,i_counter,r_counter,d_counter]+daily.patches
    return stack

fig.canvas.mpl_connect('button_press_event', onClick)
ani = animation.FuncAnimation(fig=fig, func=animate, frames=100000000, interval=1, init_func=init, blit=True)
plt.show()