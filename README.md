# PyMatting Interactive Tool
The PyMatting Interactive Tool is an interactive alpha matting tool.

# Install
Tested on Ubuntu 20.04 using Python 3.8.2.
First, install the prerequisites:

```bash
sudo apt-get install python3-pip python3-venv python3-pyqt5 git
```

Clone this GitHub repository:

```bash
git clone https://github.com/pymatting/pymatting-interactive-tool
cd pymatting-interactive-tool
```

If you want to install everything in a virtual environment, you could do it like the following:

```bash
python3 -m venv ~/envs/pit/
source ~/envs/pit/bin/activate
pip3 install -r requirements.txt
```

# Run 
To run the program, simply execute:

```bash
python3 main.py
```

# Tests
Running the tests may take a while

```bash
pip3 install -r requirements-test.txt
python3 -m unittest discover -s tests
```