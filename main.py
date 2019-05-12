from simulation import Simulation

if __name__ == "__main__":
    sim = Simulation(10000)
    # sim.map.display()
    # sim.map.display(sim.map.get_around(0, 0, 3))
    sim.play()
