# Herbivory Response Analysis via the Ising Model
A short-term biological modelling research project performed under the supervision of [Mikael Pontarp](https://portal.research.lu.se/en/persons/mikael-pontarp), a theoretical ecologist at Lund Univeristy, for my master's in bioinformatics. The project concerns the effect of signal responsiveness on fitness of a spatially-distributed, neighbour-interacting plant population under different herbivory conditions. This form of neighbour-neighbour interaction is well-suited to be modelled by the [Ising Model](https://en.wikipedia.org/wiki/Ising_model): a short range interaction lattice model originally developed to understand magnetism.

# Simulation
The Ising Model is simulated, with spin down (blue) representing an inactive defense state, and spin up (red) representing an active one. The defense state of an individual which has not been attacked randomly flips over time with a probability governed by two parameters: the defense states of the nearest neighbours, and a stochaistic effect (signal responsiveness).

On top of the Ising Model, a herbivore population is simulated as single points which travel (mostly) randomly about the lattice. They attack periodically (with some variation) which immediately forces the plant attacked (current grid cell of the herbivore) to be in an active defense state. The herbivores are designed avoid regions with high defense activity, and currently die if they attack an individual which is in an active defense state.

https://github.com/user-attachments/assets/a6624752-6f35-483a-9e20-7ab0ca887aa0
