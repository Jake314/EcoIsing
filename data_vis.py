import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/5x125-325.csv")
df["ratio"] = df.activity/df.undefended_attacks
# df["activity"] /= df["activity"].max()
# df["undefended_attacks"] /= df["undefended_attacks"].max()
# ax1 = df.plot(
#     kind="scatter", x="temp", y="time",
#     color=df.activity, colorbar=True, colormap="seismic",
#     title="Time to Defend vs. Signal Responsiveness",
#     xlabel="Signal Responsiveness", ylabel="Herbivore Half Life (s)")
ax1 = df.plot(
    kind="scatter", x="temp", y="ratio",
    title="Defense Efficiency Ratio vs. Signal Responsiveness",
    xlabel="Signal Responsiveness", ylabel="Defense Activations per Undefended Attack",
    color=df.time, colorbar=True
)

plt.show()