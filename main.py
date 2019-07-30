from simulation import Simulation

if __name__ == "__main__":
    nb_bots = 100  # nb de bot a faire spawn au debut
    sim = Simulation(nb_bots)
    # sim.map.display()
    # sim.map.display(sim.map.get_around(0, 0, 3))
    sim.play()
