# Crunchyroll Downloader

Crunchyroll downloader is a script to get the cookies required and create a `youtube_dl` command to
download a specified crunchyroll video.

Note: This is by no means a finished piece of software. If there is demand, send me a message here on github and I'll do my best to help/fix it.

## Requirements

### Red Hat Based Linux:

Chromedriver needs to be installed in order to obtain the cookies to bypass cloudflare and login. This can be obtained with

```bash
sudo dnf install chromedriver
```
Note, you also need chrome in order for this to work. (Possibly chromium but I haven't tested this.

Python packages can be installed with:

```bash
pip install -r requirements.txt
```

I suggest that this is done from inside a python virtualenv

```bash
sudo dnf install python3-virtualenvwrapper
mkvirtualenv --python=`which python3` crunchyroll_dl
```
then whenever you want to use that virtualenv again:

```bash
workon crunchyroll_dl
```