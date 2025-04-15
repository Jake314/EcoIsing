# Herbivory Response Analysis via the Ising Model
A short-term biological modelling research project performed under the supervision of [Mikael Pontarp](https://portal.research.lu.se/en/persons/mikael-pontarp), a theoretical ecologist at Lund Univeristy for my master's in bioinformatics. The project concerns the dynamics of herbivory on an unchanging plant population, whereby the induced defense mechanism can be signalled to neighbouring plants. This form of neighbour-neighbour interaction is well-suited to be modelled by the [Ising Model](https://en.wikipedia.org/wiki/Ising_model): a short range interaction lattice model originally developed to understand magnetism.

# Simulation
The Ising Model is simulated, with spin down (blue) representing an inactive defense state, and spin up (red) representing an active one. The defense state of an individual randomly flips over time with a probability governed by three parameters: the background signal (and the individual's tendency to align with it), the defense states of the nearest neighbours, and a stochaistic effect (normally referred to as temperature).

On top of the Ising Model, a herbivore is simulated as a single point which travels randomly about the lattice. It attacks periodically (with some random variation) which immediately forces the plant attacked (current grid cell of the herbivore) to be in an active defense state.

https://github.com/user-attachments/assets/d096d36f-d670-4fd4-ba82-8a3ddb2f023a
