#!/usr/bin/env python

"""
read configuration file and print the assignments for a bash script
The idea comes from
https://serverfault.com/questions/345665/how-to-parse-and-convert-ini-file-into-bash-array-variables
which came from https://stdiff.net/MB2019051301.html
"""

import click
from configparser import ConfigParser

@click.command()
@click.option("--ini", default="config.ini", type=str)
def parse_configuration(ini:str):
    config = ConfigParser()
    config.read(ini)

    for sec in config.keys():
        print("declare -A %s" % (sec))
        for k,v in config.items(sec):
            print("%s[%s]=%s" % (sec, k,v))

if __name__ == "__main__":
    parse_configuration()
