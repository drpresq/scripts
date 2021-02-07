#!/usr/bin/python3
import subprocess
import re
import argparse
import logging
import sys

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


def write_conf(conf_path: str, conf_file: str, content: [str]) -> None:
    try:
        logging.log(logging.DEBUG, f"Updating contents of {conf_path}{conf_file}")
        with open(f"{conf_path}{conf_file}", "w") as f:
            f.write("\n".join(content))
    except PermissionError:
        logging.log(logging.FATAL, f"Access Denied to: '{conf_path}{conf_file}'. Are you root?\n")
        sys.exit(-1)


def update_grub(conf_path: str, switch: bool) -> None:
    file_name: str = "grub"
    cmd_node: str = "quiet splash"
    grub_nodes: [str] = ["GRUB_CMDLINE_LINUX_DEFAULT="]

    conf = read_conf(conf_path, file_name)

    found_nodes: [str] = []
    for i, line in enumerate(conf):
        for node in [node for node in grub_nodes if node not in found_nodes]:
            pattern = f'{node}.*'
            logging.log(logging.DEBUG, f'Searching for {node} on line {i + 1} of {conf_path}{file_name}')
            found = re.match(pattern, line)
            if found and f'{cmd_node}' in found.group():
                found_nodes.append(node)
                if f'{cmd_node}' in found.group() and not switch:
                    logging.log(logging.INFO, f'Line {i + 1}: {found.group()}\talready set')
                elif f'{cmd_node} ' in found.group():
                    conf[i] = conf[i].replace(f'{cmd_node} ', f'')
                    logging.log(logging.INFO, f'Line {i + 1}: {found.group()}\tchanged to\t{conf[i]}')
                else:
                    conf[i] = conf[i].replace(f'{cmd_node}', f'')
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

    parser = argparse.ArgumentParser(description="Toggle Splash Screen Tool",
                                     epilog="A Script By George\nhttps://www.github.com/drpresq/scripts\n")

    parser.add_argument('-d',
                        action='store_true',
                        help='Disable Splash (Default Behavior)')
    parser.add_argument('-e',
                        action='store_true',
                        help='Enable Splash')
    parser.add_argument('-v',
                        action='store_true',
                        help='Verbose Logging')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.v else logging.INFO
    logging.basicConfig(level=log_level)

    if args.e:
        logging.log(logging.WARN, f'**** ENABLING Splash Screen For this System ****\n')
        update_grub(grub_conf_path, False)
        logging.log(logging.INFO, f'**** Splash Screen is now ENABLED ****\n')
    else:
        logging.log(logging.WARN, f'**** DISABLING Splash Screen For this System ****\n')
        update_grub(grub_conf_path, True)
        logging.log(logging.INFO, f'**** Splash Screen is now DISABLED ****\n')
