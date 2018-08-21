import argparse
import os

parser = argparse.ArgumentParser(description='Simple cli app to run the bot')
parser.add_argument('mode', type=str, 
                    help='Mode to run bot in. Options are "dev" for development mode and ' 
                         '"prod" for production. The difference is in the bot that is ' 
                         'used.', 
                    choices=['prod', 'dev'])
parser.add_argument('method', type=str, 
                    help='Method to use to run bot. Options are "poll" and "hook", which '
                         'use polling and a webhook, respectively.', 
                    choices=['poll', 'hook'])
ARGS = parser.parse_args()

os.environ.setdefault('RUNNING_MODE', ARGS.mode)