#!/bin/bash

# dunplicate the database for UTA100 race data
cp uta100_2024.db3 uta100_nodes.db3

# assign the write permission to the group user
chmod g+w uta100_nodes.db3

# simplify the table struture
sqlite3 uta100_nodes.db3 < post_data_grab.sql
