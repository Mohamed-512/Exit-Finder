"""
Developed by Mohamed Ashraf
https://github.com/Mohamed-512

Using https://github.com/Mohamed-512/Flexible_Neural_Net - which has more than 1600 installs through pip - this game
was made to play itself, but you control it's parameters.
"""

import tkinter as tk
import random, os, time
import flexiblenn
import winsound

"""
Global variables here
"""
window = tk.Tk()
window.resizable(False, False)
window.title("Exit Finder")
canvas_height, canvas_width = 500, 600
window.geometry("%dx%d+%d+%d" % (canvas_width, canvas_height, window.winfo_x() + 600, window.winfo_y() + 100))

fps = 60
game_speed = 1.75

box_length = 40
box_speed = 2.75 * game_speed

canvas = tk.Canvas(window, height=canvas_height, width=canvas_width, bg='grey')
canvas.pack()

obstacle_opening_length = 100
obstacle_thickness = 5
obstacle_speed = 1 * game_speed
obstacles_per_frame = int(canvas_height / 166) # designed to have 3 obstacles at once in a 500 dp high canvas


def clipped_line(num):
    """
    :param num: any number
    :return: same number but clipped between 1 and -1
    """
    return 1 if num > 1 else -1 if num < -1 else num


def play_sound_effect(is_collision):
    """
    :param is_collision: boolean variable. True if box collided with an obstacle
    :return: None
    Just plays a sound track for each pass or collision (FOR WINDOWS OS ONLY)
    """
    if is_collision:
        winsound.PlaySound("sounds/wrong.wav", winsound.SND_ASYNC | winsound.SND_FILENAME)
    else:
        winsound.PlaySound("sounds/correct.wav", winsound.SND_ASYNC | winsound.SND_FILENAME)


class Obstacle:
    """
    Class to make instances of and generate New Onstacles
    Each obstacle is just two lines with space between them defined in 'obstacle_opening_length'
    The opening position is generated randomly
    """
    def __init__(self):
        self.left_open = int(random.random() * (canvas_width - 2 * obstacle_opening_length) + obstacle_opening_length)
        self.right_open = self.left_open + obstacle_opening_length

    def make(self, offset_y):
        l1 = canvas.create_line(0, offset_y, self.left_open, offset_y, fill='black', width=obstacle_thickness)
        l2 = canvas.create_line(self.right_open, offset_y, canvas_width, offset_y, fill='black', width=obstacle_thickness)
        return [l1, l2]


def make_box(length):
    """
    :param length: The length of one side of the box to be made
    :return: None

    Box is to be initialized in the bottom 90% of the canvas
    """
    b = canvas.create_rectangle(int(canvas_width * 0.5 - length / 2), int(canvas_height* 0.9 - length / 2),
                           int(canvas_width * 0.5 + length / 2), int(canvas_height * 0.9 + length / 2), fill='white')
    return b


def move_obj(obj, delta_x, delta_y):
    """
    :param obj: Canvas object/draing
    :param delta_x: amount to move horizontally
    :param delta_y: amount to move vertically
    :return: None
    Movement is proportional to game speed
    """
    canvas.move(obj, delta_x * game_speed, delta_y * game_speed)


def did_collide_with_right_bounds(b, a):
    """
    :param b: box canvas object/draing
    :param a: obstcale[1] or the right line of the obstacle
    :return: True if they overlap else False
    """
    a = canvas.bbox(a)
    b = canvas.bbox(b)
    if (b[2] in range(a[0] + obstacle_thickness, a[2]) or b[0] in range(a[0] + obstacle_thickness, a[2])) \
            and a[1] + obstacle_thickness in range(b[1], b[3]):
        return True
    return False


def did_collide_with_left_bounds(b, a):
    """
    :param b: box canvas object/draing
    :param a: obstcale[0] or the left line of the obstacle
    :return: True if they overlap else False    """
    a = canvas.bbox(a)
    b = canvas.bbox(b)
    if b[0] in range(a[0], a[2] - obstacle_thickness) and a[1] + obstacle_thickness in range(b[1], b[3]):
        return True
    return False


def remove_old_incoming_obstacle():
    """
    :return: None

    Just removes the incoming obstacle and to do so each line -the left and right- of the obstacle is separately deleted
    then it's set as None in the obstacles list
    """
    canvas.delete(incoming_obstacle[0])
    canvas.delete(incoming_obstacle[1])
    obstacles[obstacles.index(incoming_obstacle)] = None


def init_nn(path):
    """
    :param path: path of a previously save fnn model
    :return: FNN model

                                    YOU CAN TWEAK YOUR fnn MODEL PARAMETERS HERE
    """
    # Inputs: Center x coordinate % of obstacle opening (float), current box middle x coordinate % (float)
    # Outputs: X coordinate % of box position to be (float)

    if os.path.exists(path):
        return flexiblenn.NeuralNet.load(path)
    else:
        return flexiblenn.NeuralNet(2, 1, 3, nodes_in_each_layer=5, learning_rate=0.15, activation_func="tanh")


def load_trained_model():
    """
    :return: an 82 % accuracy trained FNN model to play this game
    """
    return flexiblenn.NeuralNet.load("82%_trained-model.pkl")


def add_new_obstacle():
    """
    :return: None
    Making a new obstacle and adding to to the obstacles list
    """
    lines = Obstacle().make(0)
    obstacles.append(lines)


def print_error_status():
    """
    :return: None
    Summing all last 100 obstacles status and printing it
    """
    global seen_obstacles_count
    seen_obstacles_count += 1
    error = (1 - sum(last_100_obstacles_status) / 100) * 100
    print("\nSeen objects", seen_obstacles_count)
    print("Error through last 100 obstacles =", error, "%\n")


def get_incoming_obstacle_opening_center():
    """
    :return: Center of the upcoming obstacle opening
    """
    incoming_obstacle_opening_left = canvas.coords(incoming_obstacle[0])[2]
    incoming_obstacle_opening_right = canvas.coords(incoming_obstacle[1])[0]
    obstacle_center_x = int((incoming_obstacle_opening_left + incoming_obstacle_opening_right) / 2)
    return obstacle_center_x


"""
Game related variables here
"""
my_nn = load_trained_model()
obstacles = []
for i in range(obstacles_per_frame):
    lines = Obstacle().make(-canvas_height / obstacles_per_frame * i)
    obstacles.append(lines)

incoming_obstacle = obstacles[0]

# To count how many collisions occurred since running
collision_count = 0
# To count how many obstacles passed/collided with since running
seen_obstacles_count = 0

# list of ints to store the passing state of the last 100 seen objects 1 if passed, 0 if collided
last_100_obstacles_status = [0] * 100
did_last_obstacle_collide = False


def main():
    global my_nn, obstacles, incoming_obstacle, collision_count, seen_obstacles_count, last_100_obstacles_status, \
           did_last_obstacle_collide

    # Generating the box
    box = make_box(box_length)

    # Getting the incoming obstacle opening center
    obstacle_center_x = get_incoming_obstacle_opening_center()

    try:
        while True:
            # updating tkinter window for the objects' new positions
            window.update_idletasks()
            window.update()

            collided = False

            # Updating each visible obstacle position and removing it if it was made None which means it needs to be
            # removed
            for obstacle in obstacles:
                if obstacle is None:
                    obstacles.remove(obstacle)
                    continue

                move_obj(obstacle[0], 0, 1 * obstacle_speed)
                move_obj(obstacle[1], 0, 1 * obstacle_speed)

            # Checking if obstacle passed the box
            if canvas.coords(incoming_obstacle[0])[1] > canvas.coords(box)[3] + 10:
                # Removing the last incoming obstacle and adding a new one
                remove_old_incoming_obstacle()
                incoming_obstacle = obstacles[1]

                # Removing the 100th status update
                last_100_obstacles_status.remove(last_100_obstacles_status[0])

                # Updating status
                if did_last_obstacle_collide:
                    collision_count += 1
                    print("\nCOLLISION! (" + str(collision_count) + ")\n")
                    last_100_obstacles_status.append(0)
                else:
                    last_100_obstacles_status.append(1)

                # Playing sound according to the success of passing the last obstacle
                play_sound_effect(did_last_obstacle_collide)
                did_last_obstacle_collide = False

                print_error_status()

                obstacle_center_x = get_incoming_obstacle_opening_center()

                add_new_obstacle()

            if did_collide_with_left_bounds(box, incoming_obstacle[0]) \
                    or did_collide_with_right_bounds(box, incoming_obstacle[1]):
                did_last_obstacle_collide = True
                collided = True

            box_center_x = int((canvas.coords(box)[0] + canvas.coords(box)[2]) / 2)

            nn_output = my_nn.test([obstacle_center_x, box_center_x])

            box_movement_magnitude = clipped_line(nn_output[0])

            # clipping movement to not exceed window's width
            if box_center_x + box_movement_magnitude + box_length / 2 > canvas_width:
                box_movement_magnitude = -0.1
            elif box_center_x + box_movement_magnitude - box_length / 2 < 0:
                box_movement_magnitude = 0.1

            move_obj(box, box_movement_magnitude * box_speed, 0)

            time.sleep(1 / fps)
    except:
        my_nn.save()


main()
