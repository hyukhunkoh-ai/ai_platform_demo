import argparse
from version.api.sql import rd


def define_argparser():
    p = argparse.ArgumentParser()
    p.add_argument(
        '--filename',
        help='result'
    )
    p.add_argument(
        '--type',
        default='delete',
        help='mode'

    )
    config = p.parse_args()

    return config


def delete_redis(config):
    rd.delete(config.filename)



if __name__ == "__main__":
    config = define_argparser()
    if config.type == 'insert':
        pass

    elif config.type == 'select':
        pass

    elif config.type == 'delete':
        print(delete_redis(config))