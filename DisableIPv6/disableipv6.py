#!/usr/bin/python3
import subprocess
import re
import argparse
import logging
import sys

sysctl_conf_path: str = "/etc/"
grub_conf_path: str = "/etc/default/"


def run_cmd(cmd: str) -> None:
    logging.log(logging.INFO, f'Running {cmd}')
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.stderr and "permission denied" in result.stderr.decode():
        logging.log(logging.FATAL, f'Access Denied when running {cmd}. Are you root?\n')
        sys.exit(-1)
    elif result.stderr and "permission denied" not in result.stderr.decode() and ("error" in result.stderr.decode() or "fail" in result.stderr.decode()):
        logging.log(logging.FATAL, f'An unspecified error when running {cmd}:\n\t{result.stderr}')
        sys.exit(-1)


def read_conf(conf_path:str, conf_file: str) -> [str]:
    logging.log(logging.INFO, f"Reading contents of {conf_path}{conf_file}")
    with open(f"{conf_path}{conf_file}", "r") as f:
        content: [str] = f.read().splitlines()
    return content


def write_conf(conf_path:str, conf_file: str, content: [str]) -> None:
    try:
        logging.log(logging.DEBUG, f"Updating contents of {conf_path}{conf_file}")
        with open(f"{conf_path}{conf_file}", "w") as f:
            f.write("\n".join(content))
    except PermissionError:
        logging.log(logging.FATAL, f"Access Denied to: '{conf_path}{conf_file}'. Are you root?\n")
        sys.exit(-1)


def temp_sysctl() -> None:
    sysctl_nodes: [str] = ["net.ipv6.conf.all.disable_ipv6=1",
                           "net.ipv6.conf.default.disable_ipv6=1",
                           "net.ipv6.conf.lo.disable_ipv6=1"]
    for node in sysctl_nodes:
        run_cmd(f'sysctl -w {node}')


def update_sysctl(conf_path: str, switch: bool) -> None:
    file_name: str = "sysctl.conf"
    sysctl_nodes: [str] = ["net.ipv6.conf.all.disable_ipv6=",
                           "net.ipv6.conf.default.disable_ipv6=",
                           "net.ipv6.conf.lo.disable_ipv6="]

    conf = read_conf(conf_path, file_name)

    found_nodes: [str] = []
    for i, line in enumerate(conf):
        for node in [node for node in sysctl_nodes if node not in found_nodes]:
            pattern = f'{node}{"[0-1]"}'
            logging.log(logging.DEBUG, f'Searching for {node} on line {i+1} of {conf_path}{file_name}')
            found = re.match(pattern, line)
            if found and int(found.group()[-1]) != int(switch):
                found_nodes.append(node)
                conf[i] = f'{node}{int(switch)}'
                logging.log(logging.INFO, f'Line {i+1}: {found.group()}\tchanged to\t{conf[i]}')
            elif found and int(found.group()[-1]) == int(switch):
                logging.log(logging.INFO, f'Line {i+1}: {found.group()}\talready set')
                found_nodes.append(node)

    if len(found_nodes) < len(sysctl_nodes):
        logging.log(logging.INFO, f'Some configuration settings are missing, adding them now.')
        logging.log(logging.DEBUG, f'The contents of found_nodes: {found_nodes}')
        logging.log(logging.DEBUG, f'The contents of sysctl_nodes: {sysctl_nodes}')
        for node in [node for node in sysctl_nodes if node not in found_nodes]:
            logging.log(logging.DEBUG, f'Adding missing configuration setting {node[:-1]} to {conf_path}{file_name}')
            conf.append(f'{node}{int(switch)}')

    write_conf(conf_path, file_name, conf)
    logging.log(logging.INFO, f"Finished with {conf_path}{file_name}\n\n")


def update_grub(conf_path: str, switch: bool) -> None:
    file_name: str = "grub"
    cmd_node: str = "ipv6.disable="
    grub_nodes: [str] = ["GRUB_CMDLINE_LINUX_DEFAULT=", "GRUB_CMDLINE_LINUX="]

    conf = read_conf(conf_path, file_name)

    found_nodes: [str] = []
    for i, line in enumerate(conf):
        for node in [node for node in grub_nodes if node not in found_nodes]:
            pattern = f'{node}.*'
            logging.log(logging.DEBUG, f'Searching for {node} on line {i + 1} of {conf_path}{file_name}')
            found = re.match(pattern, line)
            if found and f'{cmd_node}' in found.group():
                found_nodes.append(node)
                if f'{cmd_node}{int(switch)}' in found.group():
                    logging.log(logging.INFO, f'Line {i + 1}: {found.group()}\talready set')
                else:
                    conf[i] = conf[i].replace(f'{cmd_node}{int(0 if switch == 1 else 1)}', f'{cmd_node}{int(switch)}')
                    logging.log(logging.INFO, f'Line {i + 1}: {found.group()}\tchanged to\t{conf[i]}')
            elif found and f'{cmd_node}' not in found.group():
                logging.log(logging.INFO, f'Adding missing configuration setting {node[:-1]} to {conf_path}{file_name}')
                found_nodes.append(node)
                conf_line = line.split('"')
                conf[i] = ''.join([conf_line[0],
                                   f'"{conf_line[1]}',
                                   f' {cmd_node}{int(switch)}"' if len(conf_line[1]) > 0 else f'{cmd_node}{int(switch)}"'])

    write_conf(conf_path, file_name, conf)
    run_cmd('update-grub')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Toggle IPv6 Tool",
                                     epilog="A Script By George\nhttps://www.github.com/drpresq/scripts\n")

    parser.add_argument('-d',
                        action='store_true',
                        help='Disable Ipv6 (Default Behavior)')
    parser.add_argument('-e',
                        action='store_true',
                        help='Enable Ipv6')
    parser.add_argument('-t',
                        action='store_true',
                        help='Disable Ipv6 temporarily (Over-rides -d)')
    parser.add_argument('-v',
                        action='store_true',
                        help='Verbose Logging')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.v else logging.INFO
    logging.basicConfig(level=log_level)

    if args.t:
        logging.log(logging.WARN, f'**** DISABLING IPv6 For this System (TEMPORARY) ****\n')
        temp_sysctl()
        logging.log(logging.INFO, f'**** IPv6 is now ENABLED ****\n'
                                  f'\t* A restart IS NOT required for this change to take effect\n'
                                  f'\t* This WILL NOT persist through the next restart\n\n')
    elif args.e:
        logging.log(logging.WARN, f'**** ENABLING IPv6 For this System ****\n')
        update_sysctl(sysctl_conf_path, False)
        update_grub(grub_conf_path, False)
        logging.log(logging.INFO, f'**** IPv6 is now ENABLED ****\n'
                                  f'\t* A restart IS required for this change to take effect\n'
                                  f'\t* This WILL persist through the next restart\n\n')
    else:
        logging.log(logging.WARN, f'**** DISABLING IPv6 For this System ****\n')
        update_sysctl(sysctl_conf_path, True)
        update_grub(grub_conf_path, True)
        logging.log(logging.INFO, f'**** IPv6 is now DISABLED ****\n'
                                  f'\t* A restart IS required for this change to take effect\n'
                                  f'\t* This WILL persist through the next restart\n\n')
