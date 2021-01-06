import argparse
import logging
import os
import sys
from configparser import ConfigParser
from chase.simulation import Simulation, config_logger

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def check_num(arg, fallback, var_name, type):
    if arg:
        try:
            num = float(arg)
        except ValueError:
            raise ValueError(f"ValueError: {var_name} "
                             f"number must be a number!")
        if num < 0:
            raise ValueError(f"ValueError: {var_name} "
                             f"number must be a positive value!")
        if type == 'int':
            return int(num)
        elif type == 'float':
            return num
        else:
            raise TypeError(f"TypeError: invalid type! "
                            f"Should be 'int' or 'float'.")
    else:
        return fallback


def parse_args():
    # create parser
    parser = argparse.ArgumentParser(description='Wolf chasing sheeps '
                                                 'simulation.')
    # add parser arguments
    parser.add_argument("-c", "--config", help="path to config file",
                        metavar='FILE')
    parser.add_argument("-d", "--dir", help="path to data directory",
                        metavar='DIR')
    parser.add_argument("-l", "--log", help="log level", metavar='LEVEL')
    parser.add_argument("-r", "--rounds", help="number of rounds",
                        metavar='NUM')
    parser.add_argument("-s", "--sheeps", help="number of sheeps",
                        metavar='NUM')
    parser.add_argument("-w", "--wait", action='store_true',
                        help="wait for a key press after finishing each round")
    # dictionary for store parsed params
    d = {}
    args = parser.parse_args()
    # init logging config if exist args.log
    if args.dir:
        d['directory'] = args.dir
        if not os.path.exists(args.dir):
            os.makedirs(args.dir)
    else:
        d['directory'] = ''

    if args.log in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        config_logger(args.log, d['directory'])
    elif args.log:
            raise ValueError('Incorrect log level argument, choose one of: '
                             'DEBUG, INFO, WARNING, ERROR, CRITICAL')

    # init simulation parameters
    if args.config:
        cfg_parser = ConfigParser()
        cfg_parser.read(args.config)
        terrain = cfg_parser['Terrain']
        movement = cfg_parser['Movement']
        try:
            arg1 = terrain.getfloat('InitPosLimit', fallback=10.0)
            arg2 = movement.getfloat('WolfMoveDist', fallback=1.0)
            arg3 = movement.getfloat('SheepMoveDist', fallback=0.5)
        except ValueError as e:
            raise ValueError('Config file error: '+str(e))
        try:
            d['init_pos_limit'] = check_num(arg=arg1,
                                            fallback=10.0,
                                            var_name='init_pos_limit',
                                            type='float')
            d['wolf_move_dist'] = check_num(arg=arg2,
                                            fallback=1.0,
                                            var_name='wolf_move_dist',
                                            type='float')
            d['sheep_move_dist'] = check_num(arg=arg3,
                                             fallback=0.5,
                                             var_name='sheep_move_dist',
                                             type='float')
        except ValueError as e:
            raise e
    else:
        d['init_pos_limit'] = 10.0
        d['wolf_move_dist'] = 1.0
        d['sheep_move_dist'] = 0.5

    try:
        d['rounds_no'] = check_num(arg=args.rounds,
                                   fallback=50,
                                   var_name='Rounds',
                                   type='int')
        d['sheeps_no'] = check_num(arg=args.sheeps,
                                   fallback=15,
                                   var_name='Sheeps',
                                   type='int')
    except ValueError as e:
        raise e

    d['wait'] = args.wait

    return d


if __name__ == "__main__":
    print(os.path.dirname(sys.argv[0]))

    try:
        d = parse_args()
    except ValueError as e:
        file_handler = logging.FileHandler(os.path.join(os.pardir,'ERROR.log'), 'w')
        formatter = logging.Formatter('%(asctime)s,%(msecs)d :: '
                                      '%(levelname)-8s :: %(message)s',
                                      '%H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.error(e)
        print(e)
        sys.exit(1)
    # create Simulation object
    simulation = Simulation(
        init_pos_limit=d['init_pos_limit'],
        sheep_move_dist=d['sheep_move_dist'],
        wolf_move_dist=d['wolf_move_dist'],
        sheeps_no=d['sheeps_no'],
        rounds_no=d['rounds_no'],
        directory=d['directory'],
        wait=d['wait']
    )

    # generate simulation
    simulation.generate_simulation()
