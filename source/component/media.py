from discord.ext import commands

from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl

import bs4 as bs
import sys
import random

from globals import video_links, image_links


class Page(QWebEnginePage):
    def __init__(self, url):
        self.app = QApplication(sys.argv)
        QWebEnginePage.__init__(self)
        self.html = ''
        self.loadFinished.connect(self._on_load_finished)
        self.load(QUrl(url))
        self.app.exec_()

    def _on_load_finished(self):
        self.html = self.toHtml(self.Callable)

    def Callable(self, html_str):
        self.html = html_str
        self.app.quit()


def refresh_video_list():
    playlist_url = "https://www.youtube.com/playlist?list=PL6ixvTgP-Rsy0Wjhz21-qJ4n42M1h4ZWZ"
    soup = bs.BeautifulSoup(Page(playlist_url).html, 'html.parser')
    for link in soup.find_all('img', width="72"):
        vid_src = link['data-thumb']
        video_id = vid_src.split('/')[4]
        if not video_id == 'img':
            video_links.append('https://www.youtube.com/watch?v=' + video_id)
    print('Video load finished')


class Media(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # This can only get a maximum of 100 videos, but it should be more than enough for what we want to get
    @commands.command(name='refreshVideos')
    async def update_videos(self):
        refresh_video_list()

    @commands.command(name='video',
                      pass_context=True)
    async def send_video(self, ctx):
        return await ctx.send(random.choice(video_links))
