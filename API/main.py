from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import json
import mysql.connector
import re

# api
app = FastAPI()
templates = Jinja2Templates(directory='jinja/')

# database
conn = mysql.connector.connect(user='subsapi', password='nLzM6KaoC50tOuKUPTvFl3WjIRYI4vac63vLwbpeCQvF5T6k', host='localhost', database='rss')
cursor = conn.cursor()

# regex
youtube_matcher = re.compile("https://www.youtube.com/channel/([^/]+)")

@app.get("/")
def root(request: Request):
    conn = mysql.connector.connect(user='subsapi', password='nLzM6KaoC50tOuKUPTvFl3WjIRYI4vac63vLwbpeCQvF5T6k', host='localhost', database='rss')
    cursor = conn.cursor()
    cursor.execute("select json_object('channel', channel_name, 'video', video_title, 'url', video_url) from videos join channels using (channel_id) where status is NULL order by video_date desc;")
    response = cursor.fetchall()
    if(len(response) == 0):
        videos = [{'No new videos': None}]
    else:
        videos = []
        for item in response:
            videos.append(json.loads(item[0]))
    return templates.TemplateResponse('subs.jinja', {'request': request, 'videos': videos})


@app.get("/add/youtube")
def add_channel(url, name, alt_name=None, status_code=201):
    conn = mysql.connector.connect(user='subsapi', password='nLzM6KaoC50tOuKUPTvFl3WjIRYI4vac63vLwbpeCQvF5T6k', host='localhost', database='rss')
    cursor = conn.cursor()
    valid_url = youtube_matcher.match(url)
    if valid_url and name:
        rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={valid_url[1]}'
        cursor.execute("select * from channels where url = %s;", (rss_url,))
        duplicate = cursor.fetchall()
        if duplicate:
            return {"status": "Value already in database",
                    "dupe": duplicate,
                    status_code: 400}
        else:
            cursor.execute("insert into channels (url, channel_name, alt_name) values (%s, %s, %s)",
                           (rss_url, name, alt_name))
            conn.commit()
            return {"status": "success", "url": url, "name": name, "alt_name": alt_name, }
    else:
        return {"status": "Invalid arguments"}
@app.get("/add")
def add_rss(url, name, alt_name=None, status_code=201):
    conn = mysql.connector.connect(user='subsapi', password='nLzM6KaoC50tOuKUPTvFl3WjIRYI4vac63vLwbpeCQvF5T6k', host='localhost', database='rss')
    cursor = conn.cursor()
    if name and url:
        cursor.execute("select * from channels where url = %s;", (url,))
        duplicate = cursor.fetchall()
        if duplicate:
            return {"status": "Value already in database",
                    "dupe": duplicate,
                    status_code: 400}
        else:
            cursor.execute("insert into channels (url, channel_name, alt_name) values (%s, %s, %s)",
                           (url, name, alt_name))
            conn.commit()
            return {"status": "success", "url": url, "name": name, "alt_name": alt_name, }
    else:
        return {"status": "Invalid arguments"}

