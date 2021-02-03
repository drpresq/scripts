#!/bin/python3

import time
from subprocess import check_output

def timeit(method):
    """ Timing Decorator Function Written by Fahim Sakri of PythonHive (https://medium.com/pthonhive) """
    def timed(*args, **kwargs):
        time_start = time.time()
        time_end = time.time()
        result = method(*args, **kwargs)
        if 'log_time' in kwargs:
            name = kwargs.get('log_name', method.__name__.upper())
            kwargs['log_time'][name] = int((time_end - time_start) * 1000)
        else:
            print('\n{}  {:5f} ms'.format(method.__name__, (time_end - time_start) * 1000))
        return result
    return timed

def system_memory_profile():
    megabyte: int = 1024000
    return [(line.split(" ")[0][0:-1], int(line.split(" ")[-2])/megabyte)
                   for line in check_output(["cat","/proc/meminfo"]).decode().splitlines()
                   if "MemTotal" in line or "MemAvailable" in line]

def system_cpu_profile():
    return [(line.split(":")[0], int(line.split(":")[1]))
             for line in check_output("lscpu").decode().splitlines()
             if "CPU(s):" in line and "NUMA" not in line or "Core(s) per socket:" in line]

@timeit
def main():

    cpu_total, core_total = system_cpu_profile()
    memory_total, memory_available = system_memory_profile()
    print("CPU:\n"
          "======================================================\n"
          "\tTotal Logical System CPU(s):\t\t{}\n"
          "\tTotal Physical System Core(s):\t\t{}\n"
          "\nMemory:\n"
          "======================================================\n"
          "\tTotal System Memory (GB):\t\t{:.2f}\n"
          "\tTotal Available System Memory (GB):\t{:.2f}".format(cpu_total[1],
                                                                   core_total[1],
                                                                   memory_total[1],
                                                                   memory_available[1]))

if __name__ == "__main__":
    main()
