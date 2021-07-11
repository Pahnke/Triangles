from point import Point
import random

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from celluloid import Camera

# TODO -  Convert it to matplotlib.animation.ArtistAnimation

def main():
    seed = 15
    random.seed(seed)

    no_points = 12
    no_partners = 2
    points = create_points(no_points, no_partners)

    colors = cm.rainbow(np.linspace(0, 1, len(points)))

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    camera = Camera(fig)

    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)

    # Error allowed in dist for it to still be converged
    allowed_diff = 3
    roundID = 1
    speed = 0.0001
    draw_rounds = 1
    keep_last_rounds = 0
    label = False
    history = []

    history.append(draw_points(points, colors, True))
    plt.pause(speed)
    camera.snap()
    print_points(points, roundID)

    while not converged(points, allowed_diff, no_partners):
        if roundID > keep_last_rounds:
            oldest = history.pop(0)
            for p in oldest:
                p.remove()

        roundID += 1
        move_points(points)

        print_points(points, roundID)

        history.append(draw_points(points, colors, label))
       # camera.snap()

       # animation = camera.animate(blit=True)
       # print(f"\nAnimated: {animation}")
       # animation.save(f"{no_points}_{seed}_{draw_rounds}_{keep_last_rounds}_animation.mp4")

        if roundID % draw_rounds == 0:
            plt.pause(speed)

    print("\nConverged")
    plt.show()

   # animation = camera.animate(blit=True)
   # print(f"\nAnimated: {animation}")
   # animation.save(f"animations/{no_points}_{seed}_{draw_rounds}_{keep_last_rounds}_animation.gif")


def move_points(points):
    moved = []
    for p in points:
        p.move(moved)
        moved.append(p)


def draw_points(points, colors, label=False):
    ps = []
    if label:
        for i in range(0, len(points)):
            ps.append(plt.scatter(points[i].coord[0], points[i].coord[1],
                    color=colors[i], label=i))
        ax = plt.gca()
        plt.legend(bbox_to_anchor=(1.1, 1.1), bbox_transform=ax.transAxes)
    else:
        for i in range(0, len(points)):
            ps.append(plt.scatter(points[i].coord[0], points[i].coord[1],
                    color=colors[i]))
    return ps


def print_points(points, roundID):
    print(f"\n----------Round: {roundID}----------\n")
    for point in points:
        partners = [p.num for p in point.partners]
        print(f"ID: {point.num}, Partners: {partners}, Coord: {point.coord}")


def converged(points, allowed_diff=2, no_partners=2):
    for p in points:
        if not p.dist_to_points_equal_dist_inbetween_points(allowed_diff):
            return False
    return True



def create_points(no_points=15, no_partners=2, dim=2):
    points = []

    for i in range(0, no_points):
        point = Point(num=i)
        point.set_coord(point.get_new_coord(dim))
        points.append(point)
    assign_partners(points, no_partners)
    return points


def assign_partners(points, no_partners=2):
    no_points = len(points)
    for p in points:
        partners_ids = get_partners_ids(no_points, p.num, no_partners)
        partners = []
        for pID in partners_ids:
            partners.append(points[pID])
        p.set_partners(partners)


def get_partners_ids(no_points, num, no_partners):
    partners_ids = []
    for _ in range(0, no_partners):
        valid = False
        while not valid:
            partner = random.randrange(0, no_points)
            if not(partner == num  or partner in partners_ids):
                valid = True

        partners_ids.append(partner)
    return partners_ids


if __name__ == "__main__":
    main()
