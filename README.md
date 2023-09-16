# gitFinder
Find a github user's email from their username

## Installation
```
 - git clone https://github.com/ByroBuff/gitFinder
 - cd gitFinder
 - pip install -r requirements.txt
```

## Usage
```
usage: gitFinder.py [-h] [-m] [-s] [-u] [-o OUTPUT] username

Find GitHub user's email(s)

positional arguments:
  username              GitHub username to search for

options:
  -h, --help            show this help message and exit
  -m, --masked          Show masked emails as well (@users.noreply.github.com emails)
  -s, --sources         Show sources of emails
  -u, --user            Only show emails linked directly to the specified account (no cross-commits)
  -o OUTPUT, --output OUTPUT
                        Output results to file
```
