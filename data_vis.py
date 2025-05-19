import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backend_bases import MouseButton
import matplotlib.patches as patches

df = pd.read_csv("results/5x125-325.csv")
df["ratio"] = df.activity/df.undefended_attacks
df["cost"] = df.activity + 0.01*df.undefended_attacks

# df["activity"] /= df["activity"].max()
# df["undefended_attacks"] /= df["undefended_attacks"].max()
# ax1 = df.plot(
#     kind="scatter", x="temp", y="time",
#     color=df.activity, colorbar=True, colormap="seismic",
#     title="Time to Defend vs. Signal Responsiveness",
#     xlabel="Signal Responsiveness", ylabel="Herbivore Half Life (s)")

# ax1 = df.plot(
#     kind="scatter", x="temp", y="cost",
#     title="Total Costs Expended vs. Signal Responsiveness",
#     xlabel="Signal Responsiveness", ylabel="A + 0.01*U",
#     color=df.time, colorbar=True
# )

# Animation Example
# fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10,5))

# coeffs = [0, 0]

# scat = ax1.scatter(df.temp, df.time - (coeffs[0]*df.activity + coeffs[1]*df.undefended_attacks))
# coef_scat = ax2.scatter(coeffs[0], coeffs[1])

# ax1.set(xlabel="Signal Responsiveness", ylabel="Energy", title="Energy vs. Responsiveness",
#         ylim=(-3000, 1000))
# ax2.set(xlabel="Cost of Activation Coefficient", ylabel="Cost of Undefended Attacks Coefficient", title="Cost Phase",
#         xlim=(0,1), ylim=(0,1))

# FRAMES=40
# SIDE=FRAMES/4
# def update(frame):
#     if frame < 10:
#         s = (frame % SIDE)/SIDE
#         coeffs = [s, 0]
#     elif frame < 20:
#         s = (frame % SIDE)/SIDE
#         coeffs = [1, s]
#     elif frame < 30:
#         s = (frame % SIDE)/SIDE
#         coeffs = [1 - s, 1]
#     elif frame < 40:
#         s = (frame % SIDE)/SIDE
#         coeffs = [0, 1 - s]
#     x = df.temp
#     y = df.time - (coeffs[0]*df.activity + coeffs[1]*df.undefended_attacks)

#     data = np.stack([x, y]).T
#     scat.set_offsets(data)

#     coef_scat.set_offsets([coeffs])
#     return (scat, coef_scat)
    
# ani = animation.FuncAnimation(fig=fig, func=update, frames=FRAMES, interval=200)
# plt.show()

fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10,5), tight_layout=True)

coeffs = [0, 0]
scat = ax1.scatter(df.temp, df.time - (coeffs[0]*df.activity + coeffs[1]*df.undefended_attacks))
ax1.set(xlabel="Signal Responsiveness", ylabel="Energy = t - C_A*A + C_U*U", title="Energy vs. Responsiveness",
        ylim=(-3000, 1000))
ax1.axhline(c="black", ls="--", alpha=0.1)

coef_scat = ax2.scatter(coeffs[0], coeffs[1], marker="X")
ax2.set(xlabel="Cost of Activation Coefficient (C_A)", ylabel="Cost of Undefended Attacks Coefficient (C_U)", title="Cost Phase",
        xlim=(0,10), ylim=(0,10))
rect = patches.Rectangle((0, 0), 1, 1, alpha=0.1, fc="black")
ax2.add_patch(rect)

moving = False
def on_click(event):
    global moving
    if event.inaxes and event.button is MouseButton.LEFT:
        moving = not moving

def on_move(event):
    if moving and event.inaxes:
        global coeffs
        coeffs = [event.xdata, event.ydata]
        coef_scat.set_offsets([coeffs])
        scat.set_offsets(np.stack([df.temp, df.time - (coeffs[0]*df.activity + coeffs[1]*df.undefended_attacks)]).T)
        plt.draw()

plt.connect("motion_notify_event", on_move)
plt.connect("button_press_event", on_click)
plt.show()