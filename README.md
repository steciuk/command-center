# Command Center

A Python/curses console application I created for my dad, who bravely switched from Windows to Linux but is still deathly afraid of the terminal.

This handy tool offers a range of utilities specially tailored for my dad:
- Schedule computer shutdown
- Automatically or manually download Polish subtitles from [napiprojekt](https://www.napiprojekt.pl/)
- Install `OTF` and `TTF` fonts in the system
- Convert `.doc`, `.docx`, `.odt`, `.odf` files to PDF
- Merge multiple PDF files into one
- Turn [Plex](https://www.plex.tv/) on or off (if installed)
- Automatically update the script via Git (if the repository has been cloned)

Unfortunately, the program is in Polish (and the instructions are more than overly verbose), adding a touch of linguistic charm to its functionality.

**I am only responsible for the damages done to my dad's computer, not yours. Proceed at your own risk.**

## Install
1. Clone the repository
```
git clone https://github.com/steciuk/command-center.git
```
2. Enter the directory
```
cd command-center
```
3. Install python3-dev package (otherwise, subtitles downloading won't work)
```
sudo apt install python3-dev
```
4. Create a virtual environment (otherwise, script updating won't work)
```
python3 -m venv .venv
```
5. Install the required python packages
```
.venv/bin/python3 -m pip install -r requirements.txt
```
6. Run the script!
```
.venv/bin/python3 main.py
```
