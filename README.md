# Scripts

## Description

---

A collection of scripts that I find useful.  Mostly written in Python 3.8 and mostly concerned with automating configuration tasks under Debian-base Linux Distributions.

## Manifest

---

* DisableIPv6:
  * **Purpose**: Disables IPv6 either temporarily or permanently
  * **Compatibility**: Debian 10 (Buster), Ubuntu 16.0
  * ****Usage****: ```./disableipv6.py --help```
  * **Status**: **Working**

* DisableSplash:
  * **Purpose**: Disables the silent startup and shutdown splash screens
  * **Compatibility**: Debian 10 (Buster), Ubuntu 16.0
  * ****Usage****: ```./disablesplash.py --help```
  * **Status**: **Working**

* SystemCheck:
  * **Purpose**: Prints general statistics about the system to the terminal (e.g. Number of Processors, amount of RAM, etc.).
  * **Compatibility**: Ubuntu 20.04, Firefox 85
  * **Usage**: `./system_check.py --help`
  * **Status**: ***Working***

* AutoAtcts:
  * **Purpose**: Automatically Downloads Custom Reports from ATCTS
  * **Compatibility**: Windows 10
  * **Usage**: see leading comments in file
  * **Status**: ***Untested***
