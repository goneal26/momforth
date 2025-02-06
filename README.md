# momforth

A cozy FORTH implementation.

Inspired by [Easy Forth](https://github.com/skilldrick/easyforth/tree/gh-pages), 
Tsoding's [Porth](https://gitlab.com/tsoding/porth) livestreams, and [Tal](https://wiki.xxiivv.com/site/uxntal.html).

Initial proof-of-concept implementation written in Python, with more coming soon.

## Usage

Run `momforth --help` for usage information. Language specification coming soon!

## Build and Run

Clone the repository with `git clone https://github.com/goneal26/momforth.git`
and navigate to the repository folder on your machine.

### Python Implementation

**Requirements**: Python 3 (I specifically used 3.13 but 3.12 should be fine)

1. Navigate to the `python` directory
2. Create a virtual environment with `python -m venv env`
3. Activate the environment (on Linux, it's `source env/bin/activate`)
4. Install requirements with `pip install -r requirements.txt`, this should 
install pyinstaller
5. Build as an executable with `pyinstaller -n momforth -F main.py`, you can then
find the executable in the `dist` directory.

> [!NOTE]
> After installing the requirements (step 4), you can simply run the program 
> with `python python/main.py` from the repository directory if you wish.

## Project Structure

- **python** contains the Python implementation
- **extras** contains extra goodies (for example, syntax highlighting)
- **examples** contains some example `.mf` scripts
