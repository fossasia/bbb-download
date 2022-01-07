from flask import Flask, request, render_template, send_file

import os
from os import path, makedirs
from zipfile import ZipFile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
import shutil

import typer
import requests
from tqdm import tqdm


def download_slides(session, base_url, base_dir, max_workers):
    xml_file = path.join(base_dir, "shapes.svg")

    tree = ET.parse(xml_file)
    root = tree.getroot()

    items = []

    for item in root:
        if href := item.attrib.get("{http://www.w3.org/1999/xlink}href"):
            items.append(href)
        if txt := item.attrib.get("text"):
            items.append(txt)

    tasks = [(session, base_url, base_dir, item) for item in items]
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        pool.map(lambda x: download(*x), tasks)


def download(session, base_url, base_dir, file_name, stream=False, force=False):
    typer.echo("Downloading " + typer.style(file_name, fg=typer.colors.BRIGHT_CYAN))
    dest_file = path.join(base_dir, file_name)

    url = base_url + file_name

    resume_at = None
    if stream:
        headers = session.head(url).headers
        filesize = int(headers.get("Content-Length") or 0)

    if not force and path.isfile(dest_file):
        # Check if file is already downloaded
        if not stream:
            return

        resume_at = Path(dest_file).stat().st_size
        if resume_at >= filesize:
            return
        else:
            typer.echo("Resuming File Download")

    headers = {}
    if resume_at:
        headers = {"Range": "bytes=%d-" % resume_at}
    res = session.get(url, headers=headers, stream=stream)
    if res.status_code != 200 and (stream and res.status_code != 206):
        typer.echo(
            typer.style(f"Error while downloading {file_name}", fg=typer.colors.RED)
        )
        return

    parent_dir = path.dirname(dest_file)

    if not path.isdir(parent_dir):
        makedirs(parent_dir)

    with open(dest_file, "ab" if resume_at else "wb") as fi:
        if stream:
            with tqdm(
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                initial=resume_at or 0,
                total=filesize,
            ) as progress:
                for data in res.iter_content(chunk_size=40960):
                    progress.update(fi.write(data))
        else:
            fi.write(res.content)


def download_meeting(url: str, meeting_id: str, chat: bool, video: bool, slides: bool, max_workers: int = 16 ):
    base_dir = path.join("presentation", meeting_id)
    if not path.isdir(base_dir):
        makedirs(base_dir)
    base_url = url + "/presentation/" + meeting_id + "/"
    data_files = [
        "metadata.xml",
        "shapes.svg",
        "panzooms.xml",
        "cursor.xml",
        "deskshare.xml",
        "presentation_text.json",
        "captions.json"
    ]

    if chat:
        data_files.append("slides_new.xml")

    with requests.session() as session:
        for file in data_files:
            download(session, base_url, base_dir, file)
        if slides:
            download_slides(session, base_url, base_dir, max_workers=max_workers)

        if video:
            medias = [
                "video/webcams.webm",
                "video/webcams.mp4",
                "deskshare/deskshare.webm",
                "deskshare/deskshare.mp4",
            ]

            for media in medias:
                download(session, base_url, base_dir, media, stream=True)

    typer.echo(typer.style("BBB Recording has been downloaded!", fg=typer.colors.GREEN))


def main(url: str, meeting_id: str, chat: bool, video: bool, slides: bool, max_workers: int = 16):
    download_meeting(url, meeting_id, chat, video, slides, max_workers=max_workers)
    createZIPAndDeleteFiles(meeting_id)

def loopOverFiles(dirName: str, zipObj):
    for folderName, subFolders, fileNames in os.walk(dirName):
            for fileName in fileNames:
                filePath = os.path.join(folderName, fileName)
                filePathArr = filePath.split('..')
                if len(filePathArr)==1:
                  zipObj.write(filePath, filePath)
                else:
                  zipObj.write(filePath, filePathArr[1])

def createZIPAndDeleteFiles(meetingId: str):
    dirName = './presentation/' + meetingId
    zipName = 'recording-' + meetingId + '.zip'
    with ZipFile(zipName, 'w') as zipObj:
        # add the folder data from presentation folder
        loopOverFiles(dirName, zipObj)
        folders = ['acornmediaplayer', 'css', 'lib']
        # add player files
        for folder in folders:
            loopOverFiles('../' + folder, zipObj)
        files = ['logo.png', 'playback.css', 'playback.js', 'playback.html']
        for file in files:
            zipObj.write('../' + file)
    shutil.rmtree(dirName)
        
def recordingExists(meeting_id: str):
    zipName = 'recording-' + meeting_id + '.zip'
    for folderName, subFolders, fileNames in os.walk('.'):
        if zipName in fileNames:
            return True
    return False

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def root():
  if request.method == 'GET':
    return render_template('index.html')
  if request.method == 'POST':
    data = request.get_json()
    url = data['server']
    server = 'https://' + url.split('/')[2]
    meeting_id = url.split('=')[1]
    try:
        if not recordingExists(meeting_id):
            main(server, meeting_id, data['chat'], data['video'], data['slides'])
        zipName = 'recording-' + meeting_id + '.zip'
        try:
            return send_file(zipName)
        except Exception as e:
            return str(e)

    except Exception as e:
        return str(e)



if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))