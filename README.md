# Overview

`githubstats` is a program to gather statistics from various github repositories and/or organizations.

# Prerequisites

`githubstats` is written in python, and should be compatible with python 2 or python 3.  Besides the built-in python libraries, it also requires the `retrying` library and the `github` library.  To install on various Linux distros:

* Ubuntu - apt-get install python-retrying python-github
* Fedora - dnf install python-retrying python-PyGithub
* Pip - pip install retrying PyGithub

# Usage

```
$ python githubstats.py -h
usage: Get sorted count of issues opened in the last year from one or more github organizations.
       [-h] [-o ORGANIZATIONS] -p PASSWORD [-s SINCE] -u USERNAME
       [-r REPOSITORIES]

optional arguments:
  -h, --help            show this help message and exit
  -o ORGANIZATIONS, --organization ORGANIZATIONS
                        organization to fetch data from; can be passed more
                        than once
  -p PASSWORD, --password PASSWORD
                        password to use for github connection
  -s SINCE, --since SINCE
                        fetch data for repositories since this date in the
                        format YYYY-MM-DD (default is 1 year ago)
  -u USERNAME, --username USERNAME
                        username to use for github connection
  -r REPOSITORIES, --repository REPOSITORIES
                        repository to fetch data from; can be passed more than
                        once
```

# Examples

Get the statistics from all repositories under the organization `ament` in the last year (the default):
```
$ python githubstats.py -u <myusername> -p <mypassword> -o ament
Getting issues for ament/ament_cmake... done
Getting issues for ament/ament_tools... done
Getting issues for ament/ament_package... done
Getting issues for ament/ament_lint... done
Getting issues for ament/sublime-ament... done
Getting issues for ament/uncrustify... done
Getting issues for ament/ament_index... done
Getting issues for ament/gmock_vendor... done
Getting issues for ament/gtest_vendor... done
Getting issues for ament/test_jenkins_test_results... done

----------------------- Most active repositories since 2016-05-23 12:58:23.734664 ------------------
Name,Total Issues,Closed Issues,Commits,Commit Comments,Issue Comments,PR Comments,Sum
ament/ament_tools,53,45,51,0,203,0,307
ament/ament_cmake,29,27,41,4,112,0,186
ament/ament_lint,25,20,35,1,107,0,168
ament/uncrustify,4,4,135,0,9,0,148
ament/ament_index,7,7,12,4,34,0,57
ament/ament_package,10,7,12,2,27,0,51
ament/gmock_vendor,3,3,8,0,6,0,17
ament/gtest_vendor,3,2,6,0,4,0,13
ament/sublime-ament,0,0,0,0,0,0,0
ament/test_jenkins_test_results,0,0,0,0,0,0,0

```

Get the statistics from just the repository `pycdlib` and `oz` in the last year (the default):
```
$ python githubstats.py -u <myusername> -p <mypassword> -r clalancette/pycdlib -r clalancette/oz
Getting issues for clalancette/pycdlib... done
Getting issues for clalancette/oz... done

----------------------- Mos>t active repositories since 2016-05-23 13:00:44.139554 ------------------
Name,Total Issues,Closed Issues,Commits,Commit Comments,Issue Comments,PR Comments,Sum
clalancette/pycdlib,2,2,256,0,5,0,263
clalancette/oz,41,32,82,3,88,0,214
```

Get the statistics from the `pycdlib` and `oz` repositories since March 1, 2017:

```
$ python githubstats.py -u <myusername> -p <mypassword> -r clalancette/pycdlib -r clalancette/oz -s 2017-03-01
Getting issues for clalancette/pycdlib... done
Getting issues for clalancette/oz... done

----------------------- Most active repositories since 2017-03-01 00:00:00 ------------------
Name,Total Issues,Closed Issues,Commits,Commit Comments,Issue Comments,PR Comments,Sum
clalancette/oz,11,7,29,3,22,0,65
clalancette/pycdlib,0,0,1,0,0,0,1
```
