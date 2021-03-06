from scipy import misc
import math


RED = 0
GREEN = 1
BLUE = 2


class Simulator(object):
    def __init__(self, small=False, map_name="data/map"):
        if small:
            self.simulation_steps_per_meter = 10
            self.map = misc.imread(map_name + '_small.png')
            self.pixels_per_meter = 10
            self.simulation_steps_per_radian = 1.0 / math.radians(4)
        else:
            self.simulation_steps_per_meter = 100
            self.map = misc.imread(map_name + '.png')
            self.pixels_per_meter = 100
            self.simulation_steps_per_radian = 1.0 / math.radians(9)
        self.map_height, self.map_width, self.colors = self.map.shape

    def reward(self, robot, robot_size, collison_reward, step_reward):
        x = robot.x
        y = robot.y

        ix = int(x * self.pixels_per_meter)
        iy = int(y * self.pixels_per_meter)
        if ix < 0 or ix >= self.map_width or iy < 0 or iy >= self.map_height:
            return collison_reward

        for i in range(int(robot_size * self.pixels_per_meter * 2)):
            for j in range(int(robot_size * self.pixels_per_meter * 2)):
                ioff = i - int(self.pixels_per_meter * robot_size)
                joff = j - int(self.pixels_per_meter * robot_size)
                if ioff * ioff + joff * joff < int(robot_size * self.pixels_per_meter) * int(robot_size * self.pixels_per_meter):
                    ix = int(x * self.pixels_per_meter) + ioff
                    iy = int(y * self.pixels_per_meter) + joff
                    if 0 <= ix < self.map_width and 0 <= iy < self.map_height:
                        if self.map[self.map_height - iy - 1][ix][0] < 10:
                            return collison_reward
        return step_reward

    def video(self, robot):
        return None

    def sense(self, robot):
        measurements = []
        for i in robot.sensors:
            measurements.append(self.sense_cone(robot, i))
        return measurements

    def action(self, act):
        return act

    def sense_cone(self, robot, sensor, relative_angle=0):
        angle_steps = max(1, int(sensor.cone_width * self.simulation_steps_per_radian))
        min_val = sensor.max_range

        for alpha in range(angle_steps):
            angle = robot.heading + sensor.heading + relative_angle + (alpha - int(angle_steps / 2.0)) / self.simulation_steps_per_radian
            dx = math.cos(angle)
            dy = math.sin(angle)

            for i in range(sensor.max_range * self.simulation_steps_per_meter):
                dist = i / float(self.simulation_steps_per_meter)
                if dist > min_val:
                    break

                x = robot.x + math.cos(robot.heading) * sensor.x - math.sin(robot.heading) * sensor.y + dx * i / float(self.simulation_steps_per_meter)
                y = robot.y + math.sin(robot.heading) * sensor.x + math.cos(robot.heading) * sensor.y + dy * i / float(self.simulation_steps_per_meter)

                ix = int(x * self.pixels_per_meter)
                iy = int(y * self.pixels_per_meter)
                if 0 <= ix < self.map_width and 0 <= iy < self.map_height:
                    if self.map[self.map_height - iy - 1][ix][RED] < 10 and self.map[self.map_height - iy - 1][ix][GREEN] < 10 and self.map[self.map_height - iy - 1][ix][BLUE] < 10 and dist < min_val:
                        min_val = dist
                        break

        return sensor.max_range if min_val == sensor.max_range else min_val
