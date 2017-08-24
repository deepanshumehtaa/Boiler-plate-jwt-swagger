# ksg-nett

This repository contains the source code for [KSG](https://www.samfundet.no/kafe-og-serveringsgjengen)'s web page. The project is written in Django.

## Quickstart

1. Create a new virtualenv with python 3.6 (instructions below)
2. Install dependencies
3. **Carefully read** [Contribution.md](https://github.com/KSG-IT/ksg-nett/blob/develop/CONTRIBUTING.md) to aid both yourself and others!

## Dependencies
* Django
* Python 3.6
* virtualenv

## Installation

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

To initialize the database, run:

```
python manage.py migrate
```

## Running

```
source venv/bin/activate
python manage.py runserver
```

## Contributing
First read [CONTRIBUTING.md](https://github.com/KSG-IT/ksg-nett/blob/develop/CONTRIBUTING.md) to understand the project guidelines. Then cgeck out [SYSTEM.md](https://github.com/KSG-IT/ksg-nett/blob/develop/SYSTEM.md) to understand the various project components.

New to this project? Check out the last section in [CONTRIBUTING.md](https://github.com/KSG-IT/ksg-nett/blob/develop/CONTRIBUTING.md) for some handy guides to get you up to speed 💪