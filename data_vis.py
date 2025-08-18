import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from scipy import stats

# Collects three dataframes from manually named outputs that the simulations performed at different herbivory levels
df1 = pd.read_csv("results/5x125-325_timelimit_lowH.csv")  # Low herbivory
df2 = pd.read_csv("results/5x125-325_timelimit.csv")  # Medium herbivory
df3 = pd.read_csv("results/5x125-325_timelimit_highH.csv")  # High herbivory
my_colours = ((0, 0, 1, 0.5), (0, 0, 0, 0.5), (1, 0, 0, 0.5))
my_labels = ("Low", "Medium", "High")

# Append a column on to each dataframe to mark its herbivory level, and combine
for i, data in enumerate([df1, df2, df3]):
    data["H"] = pd.Series([i] * data.shape[0])  # An array of one number, the exact length of the dataframe
df = pd.concat([df1, df2, df3])

# Create a 1x2 plot. Left is data, right is cost vector
fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10,5), tight_layout=True)

# The cost vector that will keep track of costs and be moved around when interacting with the plot
cost_vector = [0, 0]

# The first scatterplot. Colours are according to herbivory level, Medium, Low, High
data_scatterplot = ax1.scatter(
    df.temp,
    -(cost_vector[0]*df.activity + cost_vector[1]*df.undefended_attacks),
    c=[my_colours[x] for x in df.H]
    )
ax1.set(
    xlabel="Signal Responsiveness",
    ylabel="Energy Usage [J] (Fitness Proxy)",
    title="Fitness vs. Responsiveness",
    xlim=(0, 5), ylim=(-3000, 1000)
    )
ax1.axhline(c="black", ls="--", alpha=0.1)  # The line at y=0

# The second scatterplot. The one interacted with for the cost vector.
cost_scatterplot = ax2.scatter(
    cost_vector[0],
    cost_vector[1],
    marker="X")
ax2.set(
    xlabel="Cost per Activation of Defences [J/activation]",
    ylabel="Cost of Damage [J/undefended attack]",
    title="Cost Phase",
    xlim=(0,1), ylim=(0,8)
    )
# Approximate region boundary between negative and mixed
X = np.arange(0, 1.1, 0.01)
Y = -8*X * (X - 2)
ax2.plot(X, Y, c="black", lw=0.6)
# Approximate region boundary between positive and mixed
X2 = np.arange(0.02, 0.2, 0.01)
Y2 = 800 * X2**2
ax2.plot(X2, Y2, c="black", lw=0.6)
# Approximate region boundary between positive and mixed
# X2 = np.arange(0, 0.022, 0.01)
# Y3 = 0.379*X2/0.022
# ax2.plot(X2, Y3, c="black", lw=0.6)

# Performs the linear regression given the current cost vector
def perform_regression():
    results = []
    keys = ("slope", "intercept", "R", "P", "SE")
    for data in [df1, df2, df3]:
        x = data.temp
        y = -(cost_vector[0]*data.activity + cost_vector[1]*data.undefended_attacks)
        results.append(dict(zip(keys, stats.linregress(x, y))))
    return results

# Starts the moving process when the cost vector plot is clicked
moving = False
def on_click(event):
    global moving
    if event.inaxes and event.button is MouseButton.LEFT:
        moving = not moving

# Moves the cost vector along with the mouse and redraws the data according to new costs
def on_move(event):
    if moving and event.inaxes:
        global cost_vector
        cost_vector = [event.xdata, event.ydata]
        cost_scatterplot.set_offsets([cost_vector])
        data_scatterplot.set_offsets(np.stack([df.temp, -(cost_vector[0]*df.activity + cost_vector[1]*df.undefended_attacks)]).T)
        plt.draw()

# Performs the linear regression when the r key is pressed
def on_press(event):
    if event.key == 'r':
        # If a regression line has already been plotted, this removes the most recent ones so there aren't several
        if len(ax1.lines) > 1:  # There is the y=0 line we don't want to remove
            for i in range(3):
                ax1.lines[-1].remove()
        results = perform_regression()
        print(results)

        for i in range(3):
            ax1.axline(
                xy1=(0, results[i]["intercept"]),
                slope=results[i]["slope"],
                c=my_colours[i],
                label=my_labels[i]
                )
        plt.draw()
        ax1.legend(title="Herbivory Level")

# Activates all of the interactive elements
plt.connect("motion_notify_event", on_move)
plt.connect("button_press_event", on_click)
plt.connect("key_press_event", on_press)

plt.show()