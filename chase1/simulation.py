import os
import logging
import csv
import json
import random
from math import dist
from types import FunctionType
from functools import wraps

logger = logging.getLogger(__name__)


def __params_str(*args, **kwargs):
    args_str = ', '.join(str(arg) for arg in args)
    kwargs_str = ', '.join(f"{key}={val}" for key, val in kwargs.items())
    if args_str and kwargs:
        args_str += f", "
    return args_str + kwargs_str


def _func_logger(func, cls=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        params = __params_str(*args, **kwargs)
        cls_name = f"{cls.__name__}." if cls else ''
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{cls_name}{func.__name__}({params}) -> {result}")
        except Exception as e:
            logger.error(e)
            raise e
        return result

    return wrapper


def _cls_logger(func):
    def wrapper(cls):
        methods = [y for x, y in cls.__dict__.items() if not x.startswith('__')
                   and type(y) == FunctionType]
        for method in methods:
            setattr(cls, method.__name__,
                    func(method, cls))
        return cls

    return wrapper


@_func_logger
def config_logger(level, dir):
    log_path = os.path.join(dir, 'chase' + '.' + 'log')
    file_handler = logging.FileHandler(log_path, 'w')
    formatter = logging.Formatter('%(asctime)s,%(msecs)d :: '
                                  '%(levelname)-8s :: %(message)s',
                                  '%H:%M:%S')
    file_handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(file_handler)


# classes
@_cls_logger(_func_logger)
class Animal:
    def __init__(self, x, y, move_dist):
        self.x = x
        self.y = y
        self._move_dist = move_dist

    @property
    def coords(self):
        return round(self.x, 3), round(self.y, 3)

    def __repr__(self):
        return (f"{self.__class__.__name__}"
                f"({self.x}, {self.y}, {self._move_dist})")


@_cls_logger(_func_logger)
class Sheep(Animal):
    def __init__(self, init_pos_limit, move_dist):
        x = random.uniform(-init_pos_limit, init_pos_limit)
        y = random.uniform(-init_pos_limit, init_pos_limit)
        super(Sheep, self).__init__(x, y, move_dist)
        self.alive = True

    def move(self) -> None:
        direction = random.choice(((1, 0), (0, 1), (-1, 0), (0, -1)))
        self.x += direction[0] * self._move_dist
        self.y += direction[1] * self._move_dist


@_cls_logger(_func_logger)
class Wolf(Animal):
    def __init__(self, move_dist):
        super(Wolf, self).__init__(0, 0, move_dist)
        self.eaten = 0

    def _closest_sheep(self, sheeps):
        distances = [dist(self.coords, sheep.coords)
                     if sheep.alive else float('inf') for sheep in sheeps]

        return distances.index(min(distances)), min(distances)

    def _chase(self, sheep, distance):
        m, n = self._move_dist, (distance - self._move_dist)

        self.x = (m * sheep.coords[0] + n * self.x) / (m + n)
        self.y = (m * sheep.coords[1] + n * self.y) / (m + n)

    def take_action(self, sheeps):
        index, distance = self._closest_sheep(sheeps)
        if self._move_dist >= distance:
            self.eaten += 1
            return index
        else:
            self._chase(sheeps[index], distance)
            return -1


@_func_logger
def to_json(data, path):
    with open(path, "w") as outfile:
        json.dump(data, outfile, indent=4)


@_func_logger
def to_csv(data, path):
    with open(path, 'w') as outfile:
        wr = csv.writer(outfile)
        for row in data:
            wr.writerow(row)


@_cls_logger(_func_logger)
class Simulation:
    def __init__(self, init_pos_limit=10.0, sheep_move_dist=0.5,
                 wolf_move_dist=1.0, sheeps_no=50, rounds_no=15,
                 directory='', wait=False):
        self.sheeps = []
        for i in range(sheeps_no):
            self.sheeps.append(
                Sheep(init_pos_limit, sheep_move_dist))
            logger.info(f"Sheep no. {i} init position: "
                         f"{self.sheeps[i].coords}")
        self.wolf = Wolf(wolf_move_dist)
        logger.info(f"Wolf init position: {self.wolf.coords}")
        self.round_no = rounds_no
        self.dir = directory
        self.wait = wait

    def __repr__(self):
        return f"Simulation_instance"

    @property
    def alive_sheeps_no(self):
        return len(self.sheeps) - self.wolf.eaten

    def _sheep_move(self) -> None:
        for idx, sheep in enumerate(self.sheeps):
            if sheep.alive:
                msg = f"Sheep no. {idx} moves from {sheep.coords} "
                sheep.move()
                msg += f"to {sheep.coords}."
                logger.info(msg)

    def _wolf_hunting(self):
        before_move = self.wolf.coords
        eaten_sheep = self.wolf.take_action(self.sheeps)
        if eaten_sheep != -1:
            self.sheeps[eaten_sheep].alive = False
            logger.info(f"Wolf ate sheep no. {eaten_sheep}")
        else:
            logger.info(f"Wolf moves from {before_move} "
                          f"to {self.wolf.coords}")
        return eaten_sheep

    def print_iter_summary(self, eaten_sheep, round):
        result = ''
        if eaten_sheep == -1:
            eaten_sheep = '-'
        if round == 1:
            h = ('Round no.:', 'Wolf position:', 'Alive sheeps no.:',
                 'No. of death sheep:')
            result = f"{h[0]:>9}{h[1]:>19}{h[2]:>20}{h[3]:>20}\n"
        s = (round, str(self.wolf.coords),
             self.alive_sheeps_no, str(eaten_sheep))
        result += f"{s[0]:9d}{s[1]:>19s}{s[2]:>20d}{s[3]:>20s}"
        print(result)

    def generate_simulation(self):
        csv_data, json_data = [], [['Round no', 'Alive sheeps no']]
        round = 1
        while round <= self.round_no and self.alive_sheeps_no != 0:
            self._sheep_move()
            eaten_sheep = self._wolf_hunting()
            self.print_iter_summary(eaten_sheep, round)
            json_data.append({
                'round_no': round,
                'wolf_pos': self.wolf.coords,
                'sheeps_pos': [sheep.coords for sheep in self.sheeps]
            })
            csv_data.append([round, self.alive_sheeps_no])
            round += 1
            input("Press Enter to continue...") if self.wait else None
        json_path = os.path.join(self.dir, 'pos.json')
        csv_path = os.path.join(self.dir, 'alive.csv')
        to_json(json_data, json_path)
        to_csv(csv_data, csv_path)

