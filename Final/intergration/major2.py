import numpy as np
import sympy as sp

def get_input(json_list):
    # Initialize the list to store average RSSI values
    average_rssi = []
    # Calculate the average RSSI for each minor or fill with -1000 if the minor key does not exist
    for minor_value in range(1, 9):
        if json_list[minor_value]:
            rssi_values = [item['RSSI'] for item in json_list[minor_value]]
            average_rssi.append(np.mean(rssi_values))
        else:
            average_rssi.append(-1000)
    return average_rssi

class ParticleFilter:
    def __init__(self, num_particles=1000):
        self.num_particles = num_particles
        self.particles = None
        self.weights = None
        self.beacons = None

    def initialize_particles(self):
        if self.beacons is None:
            raise ValueError("Beacons must be set before initializing particles.")
        x_min, y_min = np.min(self.beacons, axis=0) - 1
        x_max, y_max = np.max(self.beacons, axis=0) + 1
        particles = np.empty((self.num_particles, 2))
        particles[:, 0] = np.random.uniform(x_min, x_max, self.num_particles)
        particles[:, 1] = np.random.uniform(y_min, y_max, self.num_particles)
        self.particles = particles
        self.weights = np.ones(self.num_particles) / self.num_particles

    @staticmethod
    def rssi_to_distance(rssi):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2  # Path loss exponent (example value for free space)
        distance = 10 ** ((tx_power - np.array(rssi)) / (10 * n))
        return distance

    @staticmethod
    def distance_to_rssi(distance):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2  # Path loss exponent (example value for free space)
        rssi = tx_power - 10 * n * np.log10(distance)
        return rssi

    def set_beacons(self, beacons):
        self.beacons = np.array(beacons)
        self.initialize_particles()

    def predict(self):
        # In this example, we assume no movement, so particles remain the same
        return self.particles

    def update(self, distances):
        if self.particles is None:
            raise ValueError("Particles must be initialized before updating.")
        self.weights.fill(1.0)
        for i, beacon in enumerate(self.beacons):
            beacon_dist = np.linalg.norm(self.particles - beacon, axis=1)
            self.weights *= np.exp(-0.5 * ((beacon_dist - distances[i]) ** 2))
        self.weights += 1e-300  # to avoid division by zero
        self.weights /= np.sum(self.weights)  # normalize

    def resample(self):
        indices = np.random.choice(np.arange(self.num_particles), size=self.num_particles, p=self.weights)
        self.particles = self.particles[indices]
        self.weights = self.weights[indices]
        self.weights /= np.sum(self.weights)

    def run(self, rssi_values, iterations=10):
        if self.beacons is None:
            raise ValueError("Beacons must be set before running the filter.")
        distances = self.rssi_to_distance(rssi_values)
        for _ in range(iterations):
            self.particles = self.predict()
            self.update(distances)
            self.resample()

        # Estimate the device location as the mean of the particles
        estimated_location = np.mean(self.particles, axis=0)
        return estimated_location

class Triangulation:
    @staticmethod
    def rssi_to_distance(rssi):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2  # Path loss exponent (example value for free space)
        distance = 10 ** ((tx_power - np.array(rssi)) / (10 * n))
        return distance

    @staticmethod
    def distance_to_rssi(distance):
        tx_power = -59  # dBm (example value for 1 meter distance)
        n = 2  # Path loss exponent (example value for free space)
        rssi = tx_power - 10 * n * np.log10(distance)
        return rssi

    def compute_dist(self, beacons, rssi_values):
        distances = self.rssi_to_distance(rssi_values)
        coords_and_dists = []
        for i, beacon in enumerate(beacons):
            coords_and_dists.append((beacon[0], beacon[1], distances[i]))
        return coords_and_dists

    def triposition(self, beacons, rssi_values):
        coords_and_dists = self.compute_dist(beacons, rssi_values)
        (xa, ya, da), (xb, yb, db), (xc, yc, dc) = coords_and_dists[:3]
        x, y = sp.symbols('x y')
        f1 = 2*x*(xa-xc) + xc**2 - xa**2 + 2*y*(ya-yc) + yc**2 - ya**2 - (dc**2 - da**2)
        f2 = 2*x*(xb-xc) + xc**2 - xb**2 + 2*y*(yb-yc) + yc**2 - yb**2 - (dc**2 - db**2)
        result = sp.solve([f1, f2], (x, y))
        locx, locy = result[x], result[y]
        return [float(locx), float(locy)]

def detect_location(rssi_values, beacons, mode="pf"):
    if mode == "pf":
        # Get the indices of the two-largest RSSI values
        largest_indices = np.argsort(rssi_values)[-2:]
        largest_beacons = [beacons[i] for i in largest_indices]
        largest_rssi_values = [rssi_values[i] for i in largest_indices]

        # Create and configure the particle filter
        pf = ParticleFilter()
        pf.set_beacons(largest_beacons)

        # Run the particle filter
        estimated_location = pf.run(largest_rssi_values)
    elif mode == "tri":
        # Use triangulation to locate the device
        tri = Triangulation()
        estimated_location = tri.triposition(beacons, rssi_values)
    else:
        raise ValueError("Unsupported mode. Use 'pf' for particle filter or 'tri' for triangulation.")

    return estimated_location


def scenarion2(json_list, mode="tri"):
    # Set beacons' location 
    beacons = np.array([[0,0], [2.6,2.67], [5.71,2.67], [9.7,2.67], [13.5,2.67], [15.1,0], [17.5,0], [16.9,3.9]])
    # Compute average rssi value 
    rssi_values = get_input(json_list)
    # Compute location by pf/tri algorithm
    location = detect_location(rssi_values, beacons, mode)
    
    return f"x: {location[0]:.2f}m, y: {location[1]:.2f}m"

