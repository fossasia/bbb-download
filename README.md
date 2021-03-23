# bbb-playback
Modified BBB Playback webapp to support any presentation host

## Download a BigBlueButton recording

1. Install dependencies

Python 3.8

```sh
pip -r requirements.txt
```

2. Run `python scripts/download_presentation.py <bbb_server_url> <recording_id>`

```sh
python scripts/download_presentation.py https://video2.eventyay.com 7145654166c22082657db53281dde109b7b2735e-1615943110349
```

[![asciicast](https://asciinema.org/a/401693.svg)](https://asciinema.org/a/401693)
