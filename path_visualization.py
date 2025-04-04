import numpy as np

class PathVisualization:
    def __init__(self, id_, x, y, z):
        self.id_ = id_
        self.x = x
        self.y = y
        self.z = z
        self.path_coords = list(zip(x, y, z))
        self.num_points = 1000

    def _create_sphere(self):
        golden_r = (np.sqrt(5.0) + 1.0) / 2.0
        golden_a = (2.0 - golden_r) * (2.0 * np.pi)
        xs, ys, zs = [], [], []

        for i in range(self.num_points):
            y = 1 - (i / (self.num_points - 1)) * 2
            radius = np.sqrt(1 - y * y)
            theta = golden_a * i
            xs.append(np.cos(theta) * radius)
            ys.append(y)
            zs.append(np.sin(theta) * radius)

        return list(zip(xs, ys, zs))

    def _split_sphere(self, sphere_coords):
        octants = {'posI': [], 'posII': [], 'posIII': [], 'posIV': [], 'negI': [], 'negII': [], 'negIII': [], 'negIV': []}
        for x, y, z in sphere_coords:
            if z > 0:
                if y > 0:
                    octants['posI' if x > 0 else 'posII'].append((x, y, z))
                else:
                    octants['posIV' if x > 0 else 'posIII'].append((x, y, z))
            else:
                if y > 0:
                    octants['negI' if x > 0 else 'negII'].append((x, y, z))
                else:
                    octants['negIV' if x > 0 else 'negIII'].append((x, y, z))
        return octants

    def _get_path_octant(self, path_row):
        x, y, z = path_row
        if z > 0:
            if y > 0:
                return 'posI' if x > 0 else 'posII'
            return 'posIV' if x > 0 else 'posIII'
        if y > 0:
            return 'negI' if x > 0 else 'negII'
        return 'negIV' if x > 0 else 'negIII'

    def _get_distance_between(self, path_coords, sphere_coords):
        px, py, pz = path_coords
        sx, sy, sz = sphere_coords
        return np.sqrt((px - sx)**2 + (py - sy)**2 + (pz - sz)**2)

    def _get_distribution_num(self, sphere_coords):
        octants = self._split_sphere(sphere_coords)
        path_map = {}
        repeat_time = -1

        for path_row in self.path_coords:
            repeat_time += 1
            path_octant = self._get_path_octant(path_row)
            sphere_coords_split = octants[path_octant]
            dist_dict = {sphere_row: self._get_distance_between(path_row, sphere_row) for sphere_row in sphere_coords_split}
            ranked_dist = sorted(dist_dict.items(), key=lambda x: x[1])[:3]
            segment_vertices = tuple(r[0] for r in ranked_dist)
            path_map[segment_vertices] = path_map.get(segment_vertices, []) + [repeat_time]

        return len(path_map)

    def get_distribution(self):
        sphere_coords = self._create_sphere()
        return self._get_distribution_num(sphere_coords)

    def format_time(self, time):
        return [t / 3600 for t in time]