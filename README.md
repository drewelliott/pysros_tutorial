# pySROS Tutorial: Custom CLI Alias

### In this tutorial, we will walk through using pySROS to create a custom script that can be run on or off box. When we run it onbox, we will configure a custom cli alias to make it as easy as possible to run.

This lab comes with a [containerlab](https://containerlab.dev) topology file that will allow you to quickly instantiate your own lab environment. However, this lab is using Nokia SROS, and requires an image and license file. 
> This lab uses Nokia SROS which requires an image and license file. Please reach out to your account team or check with the [containerlab discord](https://discord.gg/vAyddtaEV9)

### Pre-requisites
In addition to [containerlab](https://containerlab.dev), you will also need to have [python3](https://python.org) and [pysros](https://documentation.nokia.com/sr/24-3/pysros/index.html) installed.

## Lab Steps

### Step 1 - Instantiate Containerlab Topology

The topology file that we will use is at the root of the repo, it is named [topo.yml](https://github.com/drewelliott/pysros_tutorial/blob/main/topo.yml)

> The first time you instantiate a lab using [containerlab](https://containerlab.dev), artifacts will be created for the lab in a directory that is named according to the lab name. Using the `-c` or `--reconfigure` flag when starting the lab will force the lab to be rebuilt without using the artifacts.

Run the following command to start the lab:
`sudo clab deploy -t topo.yml -c`

You will know that the topology is fully active when you see a table similar to the following:

```+---+------------------+--------------+-------------------------------+---------------+---------+--------------+--------------+
| # |       Name       | Container ID |             Image             |     Kind      |  State  | IPv4 Address | IPv6 Address |
+---+------------------+--------------+-------------------------------+---------------+---------+--------------+--------------+
| 1 | clab-pysros-srl  | 20a1b681a458 | ghcr.io/nokia/srlinux:23.10.1 | nokia_srlinux | running | 10.5.5.6/24  | N/A          |
| 2 | clab-pysros-sros | 230c74709dab | vr-sros:23.7.R2               | nokia_sros    | running | 10.5.5.5/24  | N/A          |
+---+------------------+--------------+-------------------------------+---------------+---------+--------------+--------------+
```

### Step 2 - Review the topology

Now that the topology has started, you can log into the SROS device and take a look at what is configured.

`ssh clab-pysros-sros`

First, take a look at this [startup config](https://github.com/drewelliott/pysros_tutorial/blob/main/sros.partial.config) that we loaded onto the device when the lab was started.

You will see that we defined our python script and then reference it in our cli alias configuration:

```[/]
A:admin@sros# admin show configuration /configure python 
    python-script "recent-commit" {
        admin-state enable
        urls ["tftp://172.31.255.29/scripts/recent-commit.py"]
        version python3
    }

[/]
A:admin@sros# admin show configuration /configure system management-interface cli 
    md-cli {
        environment {
            command-alias {
                alias "recent-commit" {
                    admin-state enable
                    python-script "recent-commit"
                    mount-point "/" { }
                }
            }
        }
    }

[/]
A:admin@sros#
```

The python scripts were mounted to the device using options from [containerlab](https://containerlab.dev) in the [topology](https://github.com/drewelliott/pysros_tutorial/blob/main/topo.yml) file - we mounted the entire [scripts](https://github.com/drewelliott/pysros_tutorial/tree/main/scripts) directory right into the sros device file system, which allows sros to access those files using the tftp:// url you see in the configuration.

You can already use the custom cli alias, and it acts like a native sros command with tab-completion and contextual awareness.

```[/]
A:admin@sros# re?   

 Aliases:
 recent-commit         - Command-alias

 Global commands:
 reset                 + Clear statistics or reset operational state

[/]
A:admin@sros# re
```

Our alias is `recent-commit` and what it does is to show us details about the most recent commit including the author, the method and what was changed.

Try running the command `recent-commit` and see what the output shows.

You will see a whole of output because the most recent commit was also the one that loaded the entire configuration, so everything will show up. 

This is rather daunting, so let's see what it looks like with some more simple changes.

### Step 3 - Make configuration changes using pySROS offbox

In the [topology](https://github.com/drewelliott/pysros_tutorial/blob/main/topo.yml) file, you probably noticed that we had another device and two links between the two devices in the topology.

By default, these are not configured in SROS, so open up another terminal and navigate to the scripts directory. 

Run the script named [configure.py](https://github.com/drewelliott/pysros_tutorial/blob/main/scripts/configure.py): `./configure.py`

All this script does is make a connection to the SROS device using NETCONF and then configure the ports and commit the changes.

After these changes, let's run the cli alias again and see what the output looks like this time.

```[/]
A:admin@sros# recent-commit 
=============================================
Details about the most recent commit
=============================================
Commit-ID:      4                             
---------------------------------------------
Timestamp       2024-04-26T17:40:07.1Z        
User            admin                         
Type            netconf                       
---------------------------------------------
# TiMOS-B-23.7.R2 both/x86_64 Nokia 7750 SR Copyright (c) 2000-2023 Nokia.
# All rights reserved. All use subject to applicable license agreements.
# Built on Tue Aug 29 13:26:59 PDT 2023 by builder in /builds/237B/R2/panos/main/sros
# Configuration format version 23.7 revision 0

# Generated 2024-04-26T17:40:07.2Z by admin from 172.31.255.29
# Commit ID 4
#   Committed 2024-04-26T17:40:07.1Z by admin (NETCONF) from 172.31.255.29

    configure {
+       port 1/1/c1 {
+           admin-state enable
+           connector {

+               breakout c1-100g
+           }
+       }
+       port 1/1/c1/1 {
+           admin-state enable
+       }
+       port 1/1/c2 {
+           admin-state enable
+           connector {
+               breakout c1-100g
+           }
+       }
+       port 1/1/c2/1 {
+           admin-state enable
+       }
    }

persistent-indices {
    description "Persistent indices are maintained by the system and must not be modified."
}

# Finished 2024-04-26T17:40:07.2Z

=============================================


[/]
A:admin@sros#
```

Now we have something a little more readable, but what if we wanted to see this information remotely without logging into the router?

Go back to your other terminal where you ran the [configure.py](https://github.com/drewelliott/pysros_tutorial/blob/main/scripts/configure.py) script and this time, run the [recent-commit.py](https://github.com/drewelliott/pysros_tutorial/blob/main/scripts/recent-commit.py) script remotely - yes, this is the exact same script that we run onbox as a cli alias, but we can run it remotely and get the exact same output.

```
╭─drew@snoopy ~/git/pysros_tutorial/scripts ‹drew› ‹venv› 
╰─$ ./recent-commit.py 
=============================================
Details about the most recent commit
=============================================
Commit-ID:      4                             
---------------------------------------------
Timestamp       2024-04-26T17:40:07.1Z        
User            admin                         
Type            netconf                       
---------------------------------------------
File: config-2024-04-26T17-40-07.1Z-4.is
-------------------------------------------------------------------------------
# TiMOS-B-23.7.R2 both/x86_64 Nokia 7750 SR Copyright (c) 2000-2023 Nokia.
# All rights reserved. All use subject to applicable license agreements.
# Built on Tue Aug 29 13:26:59 PDT 2023 by builder in /builds/237B/R2/panos/main/sros
# Configuration format version 23.7 revision 0

# Generated 2024-04-26T17:40:07.2Z by admin from 172.31.255.29
# Commit ID 4
#   Committed 2024-04-26T17:40:07.1Z by admin (NETCONF) from 172.31.255.29

    configure {
+       port 1/1/c1 {
+           admin-state enable
+           connector {
+               breakout c1-100g
+           }
+       }
+       port 1/1/c1/1 {
+           admin-state enable
+       }
+       port 1/1/c2 {
+           admin-state enable
+           connector {
+               breakout c1-100g
+           }
+       }
+       port 1/1/c2/1 {
+           admin-state enable
+       }
    }

persistent-indices {
    description "Persistent indices are maintained by the system and must not be modified."
}

# Finished 2024-04-26T17:40:07.2Z

===============================================================================

=============================================
╭─drew@snoopy ~/git/pysros_tutorial/scripts ‹drew› ‹venv› 
╰─$
```

