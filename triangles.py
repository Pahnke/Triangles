from point import Point
import random

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from celluloid import Camera

# TODO -  Convert it to matplotlib.animation.ArtistAnimation

def main():
    # With current config, it doesn't converge or loop (within 5500 rounds)
    seed = 8
    random.seed(seed)

    no_points = 5
    no_partners = 2
    points = create_points(no_points, no_partners)

    colors = cm.rainbow(np.linspace(0, 1, len(points)))

    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    camera = Camera(fig)

    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)

    # Error allowed in dist for it to still be converged
    allowed_diff = 0.5

    # Useful if randomness is removed
    break_on_loop = True
    check_for_loop = True

    roundID = 1
    speed = 0.0001
    draw_rounds = 1
    keep_last_rounds = 0
    label = False

    plotted_point_history = []
    line_history = []
    if check_for_loop:
        coord_history = [[p.coord for p in points]]

    should_draw_triangles = True

    plotted_point_history.append(draw_points(points, colors, True))

    if should_draw_triangles:
        line_history.append(draw_triangles(points, colors))

    plt.pause(speed)
    camera.snap()
    print_points(points, roundID)

    while not converged(points, allowed_diff, no_partners):
        if roundID > keep_last_rounds:
            oldest = plotted_point_history.pop(0)
            for p in oldest:
                p.remove()

        roundID += 1
        move_points(points)

        print_points(points, roundID)

        plotted_point_history.append(draw_points(points, colors, label))
        if should_draw_triangles:
            for line in line_history.pop(0):
                line.remove()
            line_history.append(draw_triangles(points, colors))
       # camera.snap()

       # animation = camera.animate(blit=True)
       # print(f"\nAnimated: {animation}")
       # animation.save(f"{no_points}_{seed}_{draw_rounds}_{keep_last_rounds}_animation.mp4")

        if roundID % draw_rounds == 0:
            plt.pause(speed)

        if check_for_loop:
            looped, coord_history, looped_round = check_loop(points, coord_history)

            if looped:
                print_looped(looped_round, roundID) 
                if break_on_loop:
                    break


    if converged(points, allowed_diff, no_partners):
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


def draw_triangles(points, colors):
    lines = []
    for i in range(0, len(points)):
        p = points[i]
        no_partners = len(points[i].partners)

        for j in range(0, no_partners):
            partner = points[i].partners[j]
            xs = [partner.coord[0], p.coord[0]]
            ys = [partner.coord[1], p.coord[1]]

            temp_lines = plt.plot(xs, ys, color=colors[i])
            [lines.append(t) for t in temp_lines]

            for k in range(j + 1, no_partners):
                other_partner = points[i].partners[k]
                xs = [partner.coord[0], other_partner.coord[0]]
                ys = [partner.coord[1], other_partner.coord[1]]

                temp_lines = plt.plot(xs, ys, color=colors[i])
                [lines.append(t) for t in temp_lines]

    return lines


def check_loop(points, history):
    current_run = [p.coord for p in points]
    for roundID in range(0, len(history)):
        match = True
        compare_round = history[roundID]

        for point in range(0, len(compare_round)):
            breaking = False
            coord = compare_round[point]

            for i in range(0, len(coord)):
                if coord[i] != current_run[point][i]:
                    breaking = True
                    break
            if breaking:
                match = False
                break
        if match:
            history.append(current_run)
            return True, history, roundID
    return False, history, -1


def print_looped(first_round, current_round):
    print(f"\n\n-----------------------------")
    print(f"----------IT LOOPED----------")
    print(f"-----------------------------\n")

    print(f"First Occurence: {first_round}")
    print(f"Latest Occurence: {current_round}\n")

    print(f"\n-----------------------------")
    print(f"-----------------------------")
    print(f"-----------------------------\n\n")


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
