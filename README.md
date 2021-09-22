# bbb-playback
Modified BBB Playback webapp to support any presentation host

## Download a BigBlueButton recording (using script)

1. Create and activate virtual environment
```sh
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies

Python 3.8

```sh
pip install -r requirements.txt
```

2. Run `python scripts/download_presentation.py <bbb_server_url> <recording_id>`

```sh
python scripts/download_presentation.py https://video2.eventyay.com 7145654166c22082657db53281dde109b7b2735e-1615943110349
```

[![asciicast](https://asciinema.org/a/401693.svg)](https://asciinema.org/a/401693)


## Download recording with player (using web GUI)

1. Enter video URL and click download button.

2. Extract the downloaded zip.

3. Run basic http server in the directory.
```sh
python3 -m http.server
```

4. Open `http://localhost:8080/playback.html` with meetingId in params. <br>
e.g. `http://0.0.0.0:8000/playback.html?meetingId=8b17c624f047b18a995c7469c2f9d3e5c4ccb560-1629196080320`

