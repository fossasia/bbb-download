from os import path, makedirs
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET

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


def download_meeting(url: str, meeting_id: str, max_workers: int = 16):
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
        "captions.json",
        "slides_new.xml",
    ]

    with requests.session() as session:
        for file in data_files:
            download(session, base_url, base_dir, file)
        download_slides(session, base_url, base_dir, max_workers=max_workers)

        medias = [
            "video/webcams.webm",
            "video/webcams.mp4",
            "deskshare/deskshare.webm",
            "deskshare/deskshare.mp4",
        ]

        for media in medias:
            download(session, base_url, base_dir, media, stream=True)

    typer.echo(typer.style("BBB Recording has been downloaded!", fg=typer.colors.GREEN))


def main(url: str, meeting_id: str, max_workers: int = 16):
    download_meeting(url, meeting_id, max_workers=max_workers)


if __name__ == "__main__":
    typer.run(main)
