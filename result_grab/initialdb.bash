#!/bin/bash

# initial the tables for UTA100 race data
sqlite3 uta100_nodes.db3 < uta100_nodes.sql

# assign the write permission to the group user
chmod g+w uta100_nodes.db3
