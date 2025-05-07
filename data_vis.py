import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/temp3.csv")
df["activity"] /= df["activity"].max()
# df["undefended_attacks"] /= df["undefended_attacks"].max()
ax1 = df.plot(
    kind="scatter", x="temp", y="time", color=df.activity, colorbar=True, colormap="seismic",
    title="Time to Defend vs. Signal Responsiveness (½ Speed)", xlabel="Signal Responsiveness", ylabel="Half Life of Herbivores (s)")

plt.show()