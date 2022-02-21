# BBB Video Exporter
The goal of this project is to enable the export of video and presentations from BigBlueButton instances. You can use this project through the commandline interface executing a script or through the user a web interface in a browser. You do not need to install the BBB video exporter on the BBB server itself. You can set it up anywhere and copy the original URL of the video you want to export into the form field of  the BBB video exporter.

## How to use BBB Video Exporter

There are two ways to use this application a) per script and b) per user web interface in a browser.

### Usage per script

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

3. Run `python scripts/download_presentation.py <bbb_server_url> <recording_id>`

```sh
python scripts/download_presentation.py https://video2.eventyay.com 7145654166c22082657db53281dde109b7b2735e-1615943110349
```

[![asciicast](https://asciinema.org/a/401693.svg)](https://asciinema.org/a/401693)


### Usage per web GUI

1. Enter video URL and click download button.

2. Extract the downloaded zip.

3. Run basic http server in the directory.
```sh
python3 -m http.server
```

4. Open `http://localhost:8080/playback.html` with meetingId in params. <br>
e.g. `http://0.0.0.0:8000/playback.html?meetingId=8b17c624f047b18a995c7469c2f9d3e5c4ccb560-1629196080320`


### Credits

* accornmediaplayer
  Copyright (C) 2010 Cristian I. Colceriu
  License: [MIT License](https://github.com/ghinda/acornmediaplayer/blob/gh-pages/MIT-LICENSE.txt)

* bbb-playback
  Copyright (c) 2012 BigBlueButton Inc.
  License: [LGPL License](https://github.com/bigbluebutton/bbb-playback/blob/develop/LICENSE)
