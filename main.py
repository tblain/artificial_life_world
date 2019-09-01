from simulation import Simulation

if __name__ == "__main__":
    nb_bots = 0  # nb de bot a faire spawn au debut
    nb_herbi = 1000  # nb de bot a faire spawn au debut

    sim = Simulation(nb_bots, nb_herbi)
    # sim.map.display()
    # sim.map.display(sim.map.get_around(0, 0, 3))
    sim.play()
