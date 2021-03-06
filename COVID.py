from person import Community, COLOR_SCHEME, CONFIG
from matplotlib import pyplot as plt
from matplotlib import colors as Colors
from matplotlib import animation, gridspec
import numpy as np

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
            bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox.expanded(1.1,1.5))
            # change here
            # bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.figure.bbox)
        a.axes.draw_artist(a)
        updated_ax.append(a.axes)

    # After rendering all the needed artists, blit each axes individually.
    for ax in set(updated_ax):
        # and here
        ax.figure.canvas.blit(ax.bbox.expanded(1.1,1.5))
        # ax.figure.canvas.blit(ax.figure.bbox)


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
    ax3 = plt.subplot(gs[2:,1])
    ax4 = plt.subplot(gs[3:, 0], frameon=False)

    ax2.xaxis.set_animated(True)
    ax2.xaxis.set_zorder(2)
    ax3.xaxis.set_animated(True)

# Setup Community
community = Community()
scat = ax1.scatter([],[],s=10)
ripple_S2I = ax1.scatter([],[], lw = 1, facecolors='none')
ripple_I2R = ax1.scatter([],[], lw = 1, facecolors='none')
ripple_I2D = ax1.scatter([],[], lw = 1, facecolors='none')
# Setup Graph
times = [0]
status_count = community.status_count()
s_data = [status_count[0]]
i_data = [status_count[1]]
r_data = [status_count[2]]
d_data = [status_count[3]]
stack = ax2.stackplot([],[],[],[])
capacity_line = ax2.hlines(y=CONFIG["CAPACITY"], xmin=0, xmax=1000, colors="w", linestyle='--', lw=1.5)
line_label = ax2.text(0,CONFIG["CAPACITY"]*1.1,"  Capacity", fontsize=10,color="w")
v_line = ax2.vlines(x=0, ymin=0, ymax=10000, colors="w")
h_line = ax2.hlines(y=CONFIG["POPULATION"], xmin=0, xmax=1000, colors="w")

# Setup Daily plot
days = [0]
daily_data = [d_data[0]]
daily = ax3.bar([],[])

# Setup Counter
s_counter = ax4.text(0.33, 0.6, "", fontweight="bold", fontsize=16, horizontalalignment='left',color=COLOR_SCHEME["S"])
i_counter = ax4.text(0.83, 0.6, "", fontweight="bold", fontsize=16, horizontalalignment='left',color=COLOR_SCHEME["I"])
r_counter = ax4.text(0.33, 0.0, "", fontweight="bold", fontsize=16, horizontalalignment='left',color=COLOR_SCHEME["R"])
d_counter = ax4.text(0.83, 0.0, "", fontweight="bold", fontsize=16, horizontalalignment='left',color=COLOR_SCHEME["D"])
s_label = ax4.text(0.3, 0.6, "Susceptible", fontsize=8, horizontalalignment='right',color=COLOR_SCHEME["S"])
i_label = ax4.text(0.8, 0.6, "Infected", fontsize=8, horizontalalignment='right',color=COLOR_SCHEME["I"])
r_label = ax4.text(0.3, 0.0, "Recovered", fontsize=8, horizontalalignment='right',color=COLOR_SCHEME["R"])
d_label = ax4.text(0.8, 0.0, "Dead", fontsize=8, horizontalalignment='right',color=COLOR_SCHEME["D"])

def init():
    # init community
    ax1.set_xlim(-CONFIG["HEIGHT"] * 1.1, CONFIG["HEIGHT"] * 1.1)
    ax1.set_ylim(-CONFIG["HEIGHT"] * 1.1, CONFIG["HEIGHT"] * 1.1)
    ax1.tick_params(left=False,labelleft=False,bottom=False,labelbottom=False)
    scat.set_offsets([])
    ripple_S2I.set_offsets([])
    ripple_I2R.set_offsets([])
    ripple_I2D.set_offsets([])

    # init graph
    ax2.set_ylim(0, CONFIG["POPULATION"])
    ax2.set_ylabel("Population",**font)
    ax2.tick_params(right=True)
    stack = ax2.stackplot([], [], [], [], [])

    # init daily plot
    ax3.set_ylabel("Daily Deaths",**font)
    ax3.tick_params(right=True)
    ax3.set_xlabel("Day",**font)
    ax3.set_ylim(0, CONFIG["POPULATION"]*0.07)
    daily = ax3.bar([], [])

    # init counter
    ax4.tick_params(left=False, bottom=False,labelleft=False, labelbottom=False)
    ax4.set_ylim()
    s_counter.set_text("")
    i_counter.set_text("")
    r_counter.set_text("")
    d_counter.set_text("")

    stack = stack+[scat,ripple_S2I,ripple_I2R,ripple_I2D,s_counter,i_counter,r_counter,d_counter]+daily.patches
    return stack

pause = False
def onClick(event):
    global pause
    pause ^= True

def animate(frame):
    if frame == 1:
        global pause
        pause = True
    if not pause:
        # Update community
        poss, colors, status, status_count, ripples_data = community.update()
        scat.set_offsets(poss)
        scat.set_color(colors)

        #update ripple
        #S2I
        if ripples_data[0].shape[0] > 0:
            ripple_S2I.set_offsets(ripples_data[0][:,:2])
            ripple_S2I.set_sizes(ripples_data[0][:, 2]*CONFIG["RIPPLE_SIZE"])
            alphas = 1-ripples_data[0][:, 2]/CONFIG["RIPPLE_DURATION"]
            rgb = Colors.to_rgb(COLOR_SCHEME["I"])
            ripple_colors = np.concatenate((np.repeat(np.array([rgb]),alphas.shape[0],axis = 0),np.vstack(alphas)),axis = 1)
            ripple_S2I.set_edgecolors(ripple_colors)
        else:
            ripple_S2I.set_offsets([])
        #I2R
        if ripples_data[1].shape[0] > 0:
            ripple_I2R.set_offsets(ripples_data[1][:,:2])
            ripple_I2R.set_sizes(ripples_data[1][:, 2]*20)
            alphas = 1-ripples_data[1][:, 2]/CONFIG["RIPPLE_DURATION"]
            rgb = Colors.to_rgb(COLOR_SCHEME["R"])
            ripple_colors = np.concatenate((np.repeat(np.array([rgb]),alphas.shape[0],axis = 0),np.vstack(alphas)),axis = 1)
            ripple_I2R.set_edgecolors(ripple_colors)
        else:
            ripple_I2R.set_offsets([])
        if ripples_data[2].shape[0] > 0:
            ripple_I2D.set_offsets(ripples_data[2][:,:2])
            ripple_I2D.set_sizes(ripples_data[2][:, 2]*20)
            alphas = 1-ripples_data[2][:, 2]/CONFIG["RIPPLE_DURATION"]
            rgb = Colors.to_rgb(COLOR_SCHEME["D"])
            ripple_colors = np.concatenate((np.repeat(np.array([rgb]),alphas.shape[0],axis = 0),np.vstack(alphas)),axis = 1)
            ripple_I2D.set_edgecolors(ripple_colors)
        else:
            ripple_I2D.set_offsets([])

        # Update Stackplot
        times.append(community.time / CONFIG["TIME_IN_DAY"])
        s_data.append(status_count[0])
        i_data.append(status_count[1])
        r_data.append(status_count[2])
        d_data.append(status_count[3])

        current_time = times[-1]
        ax2.set_xlim(0, current_time)
        ax3.set_xlim(0, current_time)

        # update daily plot
        if int(current_time) - current_time == 0.0:
            days.append(current_time)
            daily_data.append(d_data[-1] - d_data[-int(CONFIG["TIME_IN_DAY"] / CONFIG["DT"]) - 1])

        # Update counter
        s_counter.set_text("{}".format(status_count[0]))
        r_counter.set_text("{}".format(status_count[2]))
        i_counter.set_text("{}".format(status_count[1]))
        d_counter.set_text("{}".format(status_count[3]))
        recovered,dead,infected = status_count[2], status_count[3],status_count[1]
        closed_case = status_count[2]+status_count[3]
        if closed_case != 0:
            print(f"Recovered in closed case: {(recovered/closed_case*100):.2f}%")
            print(f"Death in closed case: {(dead / closed_case * 100):.2f}%")
            print(f"Death rate: {(dead / (closed_case+infected) * 100):.2f}%")
            print(f"Infected rate: {((closed_case + infected)/CONFIG['POPULATION'] * 100):.2f}%")
            print("-----------------")

    # resample
    times_s = np.array(times)
    i_data_s = np.array(i_data)
    s_data_s = np.array(s_data)
    r_data_s = np.array(r_data)
    d_data_s = np.array(d_data)
    if times_s.shape[0] > CONFIG["RESAMPLE_SIZE"] and times_s.shape[0]%CONFIG["RESAMPLE_SIZE"]==0:
        bin_size = int(times_s.shape[0]/CONFIG["RESAMPLE_SIZE"])
        samples_index = np.mod(np.arange(times_s.shape[0]),bin_size) == 0
        times_s = times_s[samples_index]
        i_data_s = np.mean(i_data_s.reshape(-1, bin_size), axis=1)
        s_data_s = np.mean(s_data_s.reshape(-1, bin_size), axis=1)
        r_data_s = np.mean(r_data_s.reshape(-1, bin_size), axis=1)
        d_data_s = np.mean(d_data_s.reshape(-1, bin_size), axis=1)

    stack = ax2.stackplot(times_s, i_data_s, s_data_s, r_data_s, d_data_s,colors=[COLOR_SCHEME["I"], COLOR_SCHEME["S"],
                                                                        COLOR_SCHEME["R"], COLOR_SCHEME["D"]])

    #filter non zero values
    daily_data_s = np.array(daily_data)
    non_zero_index = daily_data_s != 0
    daily_data_s = daily_data_s[non_zero_index]
    days_s = np.array(days)[non_zero_index]
    daily = ax3.bar(days_s, daily_data_s, color=COLOR_SCHEME["D"])
    stack = [ax2.xaxis,ax3.xaxis,v_line,h_line,
             scat,ripple_S2I,ripple_I2R,ripple_I2D,capacity_line,line_label,
             s_counter,i_counter,r_counter,d_counter] + daily.patches + stack
    return stack


fig.canvas.mpl_connect('button_press_event', onClick)
ani = animation.FuncAnimation(fig=fig, func=animate, frames=100000000, interval=1, init_func=init, blit=True)
plt.show()