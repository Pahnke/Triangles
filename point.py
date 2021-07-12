import math
import random

class Point:

    def __init__(self, num,
            coord=None,
            partners=None,
            step=0.25,
            error_radius = 0.0,
            flip_triangle_rate=0.0,
            allowed_closeness = 7.5,
            stepping_error = 0.0,
            verbose=False):

        self.num = num
        self.set_partners(partners)
        self.set_coord(coord)
        # Distance travelled towards the ideal spot per turn
        self.step = step
        # step = step + Uniform(0, stepping_error)
        # So points will move towards it at different rates
        self.stepping_error = stepping_error
        # The ideal coord will get Uniform(0, Error_Radius)
        # added to it
        self.error_radius = error_radius
        # 2 Triangles can be formed, this is the rate that they
        # aim for the offer triangle
        self.flip_triangle_rate = flip_triangle_rate
        self.top_triangle = False
        # Points can only be allowed_closeness to another point
        # This is used for finding the spot the point wants to be at
        # and is currently ignored when the point is moving (TODO)
        self.allowed_closeness = allowed_closeness
        # If a point is too close to another point,
        # this is the step it takes to try to move away from it
        self.wriggle_step = 0.1
        # bounds = [section]
        # section = [boundary_coord]
        # boundary_coord = Bool: has_to_be_greater_than,
        # coord[0], coord[1], ...
        # On the boundary is allowed
        self.bounds = [[[True, 0.0, 0.0], [False, 100.0, 100.0]]]
        # Print debugging info
        self.verbose = verbose


    def set_coord(self, coord):
        if coord is None:
            return
        self.coord = coord
        self.dim = len(coord)

    def set_partners(self, partners):
        if partners is None:
            return
        self.partners = partners
        self.no_partners = len(partners)

        self.calculate_inbetween_partner_dists()
        self.calculate_dist_to_partners()

    def calculate_inbetween_partner_dists(self):
        self.inbetween_partner_dists = []

        for i in range(0, self.no_partners):
            dist = self.abs(
                    self.partners[i].coord,
                    self.partners[(i + 1) % self.no_partners].coord
                    )
            self.inbetween_partner_dists.append(dist)

    def calculate_dist_to_partners(self):
        self.dist_to_partners = []

        for p in self.partners:
            dist = self._dist_to_point(p.coord)
            self.dist_to_partners.append(dist)


    def move(self, new_points):
        self._try_to_flip()

        self._set_ideal_spot(new_points)

        if self.verbose:
            print(f"\nID: {self.num}")
            print(f"True Ideal: {self.ideal_spot}")

        # Makes it so ideal spot is a valid spot
        # While moving to the ideal spot, points may move over
        # another point
        attempts = 0
        while not self._valid_spot(self.ideal_spot, new_points):
            # Tries the other triangle, if it fails goes back
            # to the original triangle
            if attempts == 0 or attempts == 1:
                self._flip()
                self._set_ideal_spot(new_points)
                if self.verbose:
                    print(f"Spot after flip: {self.ideal_spot}")
            else:
                try:
                    self.ideal_spot = self._fix_spot(
                            self.ideal_spot, new_points)
                    if self.verbose:
                        print(f"Spot after fixing: {self.ideal_spot}")

                except RecursionError:
                    self.ideal_spot = self._random_spot(
                            len(self.ideal_spot),
                            new_points)
                    if self.verbose:
                        print(f"Recursion Error, rand spot: {self.ideal_spot}")
            attempts += 1

        self._step_to_point()

    def _step_to_point(self):
        error = random.uniform(0, self.stepping_error)
        dist = self.step + error
        self._move_to_point(dist)

    def _jump_to_point(self):
        dist = self._dist_to_point(self.ideal_spot)
        self._move_to_point(dist / self.step)

    def _move_to_point(self, total_move):
        direction = []
        for i in range(0, self.dim):
            d = self.ideal_spot[i] - self.coord[i]
            direction.append(d)
        zeros = [0.0 for _ in range(0, self.dim)]
        size_direction = self.abs(zeros, direction)

        new_coord = []
        if total_move > size_direction:
            dir_scalar = 1.0
        else:
           dir_scalar = total_move / size_direction

        for i in range(0, self.dim):
            scaled_d = direction[i] * dir_scalar
            c = self.coord[i] + scaled_d
            rc = self.add_error_radius(c)
            new_coord.append(rc)

        self.coord = new_coord

    def add_error_radius(self, point):
        error = random.uniform(-self.error_radius, self.error_radius)
        return point + error

    def _set_ideal_spot(self, new_points):
        if self.no_partners == 2:
            self.ideal_spot = self._get_ideal_spot_two_partners(
                    new_points)
        else:
            # TODO
            raise Exception(f"No. Partners: {self.no_partners} not supported")

    def _flip(self):
        self.top_triangle = not self.top_triangle

    def _try_to_flip(self):
        if random.random() < self.flip_triangle_rate:
            self._flip()

    def _valid_spot(self, spot, new_points):
        if self._too_close(spot, new_points):
            return False
        elif self._out_of_bounds(spot):
            return False

        return True

    def _out_of_bounds(self, spot):
        for section in self.bounds:
            in_this_section = True
            for b in section:
                bound_coord = b[1:]
                has_to_be_greater = b[0]
                n = min(len(bound_coord), len(spot))

                for i in range(0, n):
                    if has_to_be_greater:
                        if spot[i] < bound_coord[i]:
                            in_this_section = False
                            break
                    else:
                        if spot[i] > bound_coord[i]:
                            in_this_section = False
                            break
            if in_this_section:
                return False
        return True

    def _too_close(self, spot, new_points):
        for p in [n.coord for n in new_points]:
            dist = self.abs(spot, p)
            if dist <= self.allowed_closeness:
                return True
        return False

    def _get_in_bounds(self, spot):
        # Manhattan dist
        min_dist_to_get_in = float('inf')
        section_going_in = -1

        for section_i in range(0, len(self.bounds)):
            section = self.bounds[section_i]
            dist_to_get_in_section = 0.0

            for boundary in section:
                has_to_be_greater = boundary[0]
                b_coord = boundary[1:]
                for i in range(0, len(b_coord)):
                    if has_to_be_greater:
                        if b_coord[i] <= spot[i]:
                            continue
                    else:
                        if b_coord[i] >= spot[i]:
                            continue

                    # Out of bounds for this point
                    dist = abs(b_coord[i] - spot[i])
                    dist_to_get_in_section += dist


            if dist_to_get_in_section < min_dist_to_get_in:
                section_going_in = section_i
                min_dist_to_get_in = dist_to_get_in_section

        return self._teleport_to_boundary(spot,
                self.bounds[section_going_in])

    def _teleport_to_boundary(self, spot, section):
        for boundary in section:
            has_to_be_greater = boundary[0]
            b_coord = boundary[1:]
            for i in range(0, len(b_coord)):
                if has_to_be_greater:
                    spot[i] = max(spot[i], b_coord[i])
                else:
                    spot[i] = min(spot[i], b_coord[i])
        return spot

    def _random_spot(self, dim, other_points):
        spot = self.get_new_coord(dim)

        while self._too_close(spot, other_points):
            spot = self._wriggle(spot)

        return spot

    def _wriggle(self, spot):
        n = random.randrange(0, len(spot))
        step = random.uniform(0, self.wriggle_step)
        spot[n] += step
        return spot

    def _fix_spot(self, spot, new_points):
        if self._out_of_bounds(spot):
            new_spot = self._get_in_bounds(spot)
            return self._fix_spot(new_spot, new_points)

        if self._too_close(spot, new_points):
            new_spot = self._wriggle(spot)
            return self._fix_spot(new_spot, new_points)

        return spot

    def _get_ideal_spot_two_partners(self, new_points):
        if self.dim > 2:
            return self._get_higher_dim_two_partner_spot()
        spot = []
        first = self.partners[0].coord
        x1 = first[0]
        y1 = first[1]

        second = self.partners[1].coord
        x2 = second[0]
        y2 = second[1]

        flip_factor = 1.0
        if self.top_triangle:
            flip_factor = -1

        s1 = (x1 + x2 + flip_factor * math.sqrt(3.0) * (y1 - y2)) / 2.0
        s2 = (y1 + y2 + flip_factor * math.sqrt(3.0) * (x2 - x1)) / 2.0

        spot.append(s1)
        spot.append(s2)

        return spot

    def _get_higher_dim_two_partner_spot(self):
        # TODO
        pass

    def abs(self, this, that):
        if not len(this) == len(that):
            raise Exception("Comparing abs of wrong dim")

        dist_squared = 0.0
        for i in range(0, len(this)):
            diff = this[i] - that[i]
            dist_squared += diff * diff

        return math.sqrt(dist_squared)

    def _dist_to_point(self, other_coord):
        return self.abs(self.coord, other_coord)

    def dist_to_points_equal_dist_inbetween_points(self, allowed_diff):
        self.calculate_dist_to_partners()
        self.calculate_inbetween_partner_dists()

        for i in range(0, self.no_partners):
            dist_to_point = self.dist_to_partners[i]
            dist_point_to_next_partner = self.inbetween_partner_dists[i]

            diff = abs(dist_to_point - dist_point_to_next_partner)
            if diff > allowed_diff:
                return False
        return True

    def get_new_coord(self, dim=2):
        coord = []
        for _ in range(0, dim):
            coord.append(self._get_coord_value())

        return coord

    def _get_coord_value(self, min_v=0.0, max_v=100.0):
        return random.uniform(min_v, max_v)
