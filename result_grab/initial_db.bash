#!/bin/bash

# initial the tables for UTA100 race data
sqlite3 uta100_2024.db3 < uta100_2024.sql

# assign the write permission to the group user
chmod g+w uta100_2024.db3
