# Herbivory Response Analysis via the Ising Model
A short-term biological modelling research project performed under the supervision of [Mikael Pontarp](https://portal.research.lu.se/en/persons/mikael-pontarp), a theoretical ecologist at Lund Univeristy, for my master's in bioinformatics. The project concerns the effect of defence-signal responsiveness on fitness of a spatially-distributed, neighbour-interacting plant population under different herbivory conditions. This form of neighbour-neighbour interaction is well-suited to be modelled by the [Ising Model](https://en.wikipedia.org/wiki/Ising_model): a short range interaction lattice model originally developed to understand magnetism.

The goal was to simulate signal communication in a plant population using the Ising model, and observe the effect that varying signal responsiveness has on fitness. The simulation of the plants and herbivores is found in isingsim.py and the data collection and presentation is handled by data_vis.py.

# Simulation
The Ising Model is simulated, with spin down (blue) representing an inactive defense state, and spin up (red) representing an active one. The defense state of an individual which has not been attacked randomly flips over time with a probability governed by two parameters: the defense states of the nearest neighbours, and a stochaistic effect (signal responsiveness).

On top of the Ising Model, an herbivore population is simulated as point particles which travel (mostly) randomly about the lattice. They attack periodically (with some variation) which immediately forces the plant attacked (current grid cell of the herbivore) to be in an active defense state. The herbivores are designed to avoid regions with high defense activity, and currently die (stop moving and attacking) if they attack an individual which is in an active defense state.

https://github.com/user-attachments/assets/a6624752-6f35-483a-9e20-7ab0ca887aa0

# Program Usage
Please note this software is not intended to be a widely distributed tool, and thus few failsafes have been implemented. Please read "Important Notes on Usage" if one wishes to use the program.
- run(Population()) runs the simulation with all default values when isingsim.py is run
- The results of the simulation are tabulated in sim.record and can be exported this way
- Running data_vis.py will aggregate the data manually specified in the first few lines and then plot them in a scatterplot of energy usage (from defence activations and undefended attacks and their costs) vs. signal responsiveness.
- A second plot to the right, cost of undefended attacks vs. cost of defence activation, can be interacted with by clicking once to lift the cost vector and clicking again to drop it. This sets the cost parameters which are used in the first graph.
- The "r" key can be pressed at any time to perform a linear regression. The regression lines are plotted and labelled, and the releveant statistics are printed in the terminal.

# Obtaining Results
Multi-runs were done to produce several data points for a single degree of herbivory. The degree was chosen by hand for each multi-run, and the output was manually named accordingly. For example "5x125-325_timelimit_lowH" indicates the signal responsiveness parameter was varied from 1.25 to 3.25, with each value being simulated 5 times. The halting condition was a time limit (as opposed to fatality limit), and the herbivory level was lower than default (half speed, double attack cooldown). The outputs were combined using Pandas in data_vis.py and displayed using Matplotlib. A graph shows the energy usage (a proxy for fitness) vs. the signal responsiveness. A second graph allows to user to select the cost vector, altering the shape of the data. Clicking once "lifts" the vector, allowing it to be moved, and clicking a second time "drops" the vector, setting the value and leaving it in place. The region boundaries in the cost phase plot were estimated by hand and hard-coded. These are not automatic, nor do they represent anything beyond a mere observation of patterns. Pressing "r" on the keyboard performs a linear regression through SciPy. The regression lines are plotted and labelled automatically, and the relevant statistics are printed to the terminal. These plots and statistics are presented in the paper.

# Important Notes on Usage
Note that this program is not meant to be a widely distributed user product. Therefore, few failsafes have been implemented as it is assumed whoever is using the program (myself primarily) knows how to use the tool properly. It is mostly a proof of concept to expound on some theory -- not a commercial product. With that said, here are some important notes one must keep in mind (myself included) when using the software (time permitted, failsafes would be implemented here):
- IMPORTANT: Interactable elements should not be dragged outside of their characteristic bounding boxes. If the thermostat is being moved and the mouse is dragged into the simulation, this will crash the program. If the cost vector is being moved and the mouse is dragged out of the plot, unexpected or unintended results may occur. If the mouse button is held down and dragged between plots or outside of the window, this may result in crashes or unintented behaviour.
- IMPORATNT: Multiple possible run commands have been written, and only one should be uncommented at a time.
- Cell states should only be +1 or -1
- Extreme or improper (negative, strings, etc.) parameter inputs have not been handled. There are default values set for every parameter, so look to these for what the values should be like and what the types should be.
- Multi-runs need to have their output named manually to avoid overwriting data.
- Data aggregation needs to have the inputs declared manually to work properly (this is found in the first few lines of data_vis.py)
- The regression key, "r", should only be tapped. Behaviour when held is undocumented and unhandled, but will likely slow down the program massively or potentially crash it.