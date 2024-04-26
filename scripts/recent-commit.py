#!/usr/bin/env python3

# This script can be run on or off box to show the most recent 
# configuration changes

# Author: Drew Elliott
# Contact: drew.elliott@nokia.com
#
# Revision History:
#   v0.1    -   April 26, 2024

from pysros.management import sros, connect
from pysros.pprint import Table

ROUTER = '10.5.5.5'
USER = 'admin'
PASS = 'admin'
PORT = 830

def get_connection(hostname: str, username: str, password: str, port: int) -> object:
    from pysros.management import connect
    from pysros.exceptions import ModelProcessingError
    import sys
    try:
        connection_object = connect(host=hostname,
                                    port=port,
                                    username=username,
                                    password=password,
                                    hostkey_verify=False)
    except RuntimeError as e1:
        print("Failed to connect.  Error:", e1)
        sys.exit(-1)
    except ModelProcessingError as e2:
        print("Failed to create model-driven schema.  Error:", e2)
        sys.exit(-2)
    return connection_object


def find_most_recent_commit(c):
    commit_response = c.running.get('/nokia-state:state/system/management-interface/configuration-region[region-name="configure"]/commit-history')
    most_recent_commit_id = max(commit_response['commit-id'].keys())
    return commit_response['commit-id'][most_recent_commit_id]
   
   
def write_output(conn_obj, onbox): 
    commit_data = find_most_recent_commit(conn_obj)
    if onbox:
        with open(commit_data['increment-location'].data, "rt") as f:
            changes = f.read()
    else:
        changes = conn_obj.cli("file show %s" % commit_data['increment-location'].data ) 
    summary = changes
    rows = [["Timestamp", commit_data['timestamp'].data], 
            ["User", commit_data['user'].data],
            ["Type", commit_data['type'].data]]
    cols = [(15, "Commit-ID:"), (30, commit_data['id'].data)]
    width = sum([col[0] for col in cols])
    table = Table("Details about the most recent commit",
                  columns=cols, showCount=None,
                  summary=summary, width=width)
    table.print(rows)


def main():
    if sros():
        c = connect()
        onbox = True
    else:
        c = get_connection(ROUTER, USER, PASS, PORT)
        onbox = False
    write_output(c, onbox)


if __name__ == "__main__":
    main()