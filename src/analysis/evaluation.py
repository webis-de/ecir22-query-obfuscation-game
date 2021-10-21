#!/usr/bin/env/python3

"""
------------------------------------------------------------------------------------------------
 @authors       Nicola Lea Libera (117073)
------------------------------------------------------------------------------------------------
 Description: This script loads the relevant data from the log file of the server and
                analyses the given data.
------------------------------------------------------------------------------------------------
"""

import pandas as pd


def main():
    dataframe = pd.read_json("nba_all_elo.csv")
    dataframe.describe(include=str)


if __name__ == '__main__':
    main()
