# -*- coding: utf-8 -*-
import scrapy
import json
import urllib.request
import os
import datetime


def getId(media):
    return media['node']['id']


class InstagramSpider(scrapy.Spider):
    name = "Instagram"  # Name of the Spider, required value

    def __init__(self, account='', videos='', images='', sidecar='', timestamp=''):
        self.videos = videos
        self.images = images
        self.sidecar = sidecar
        self.account = account

        self.start_urls = ["https://www.instagram.com/" + self.account]

        self.savedir = "@" + self.account

        if timestamp == 'y':
            self.savedir = self.getCurrentTime() + self.savedir

        if not os.path.exists(self.savedir):
            os.makedirs(self.savedir)

    # Entry point for the spider
    def parse(self, response):
        request = scrapy.Request(response.url, callback=self.parse_page)
        return request

    # Method for parsing a page
    def parse_page(self, response):
        # We get the json containing the photos's path
        js = response.selector.xpath(
            '//script[contains(., "window._sharedData")]/text()'
        ).extract()
        js = js[0].replace("window._sharedData = ", "")
        jscleaned = js[:-1]

        # Load it as a json object
        locations = json.loads(jscleaned)
        # We check if there is a next page
        user = locations['entry_data']['ProfilePage'][0]['graphql']['user']
        is_private = user['is_private']

        if is_private:
            print("!!!!! Error !!!! : Looks like a private account")
            return

        has_next = (
            user['edge_owner_to_timeline_media']['page_info']['has_next_page'] or
            user['edge_saved_media']['page_info']['has_next_page'] or
            user['edge_media_collections']['page_info']['has_next_page'] or
            user['edge_related_profiles']['page_info']['has_next_page']
        )
        medias = user['edge_owner_to_timeline_media']['edges']
        medias += user['edge_saved_media']['edges']
        medias += user['edge_media_collections']['edges']
        medias += user['edge_related_profiles']['edges']
        if self.videos == 'y':
            medias += user['edge_felix_video_timeline']['edges']
            has_next = (
                has_next or
                user['edge_felix_video_timeline']['page_info']['has_next_page']
            )

        medias.sort(key=getId)

        # We parse the photos
        for media in medias:
            node = media['node']
            url = node['display_url']
            id = node['id']
            type = node['__typename']
            code = node['shortcode']

            if type == "GraphSidecar" and self.sidecar == 'y':
                yield scrapy.Request(
                    "https://www.instagram.com/p/" + code,
                    callback=self.parse_sideCar
                )

            elif type == "GraphImage" and self.images == 'y':
                yield scrapy.Request(
                    url,
                    meta={'id': id, 'extension': '.jpg'},
                    callback=self.save_media
                )

            elif type == "GraphVideo" and self.videos == 'y':
                yield scrapy.Request(
                    "https://www.instagram.com/p/" + code,
                    callback=self.parse_page_video
                )

        # If there is a next page, we crawl it
        if has_next:
            url = "https://www.instagram.com/" + self.account + "/?max_id=" + medias[-1]['node']['id']
            yield scrapy.Request(url, callback=self.parse_page)

    # Method for parsing a video_page
    def parse_page_video(self, response):
        # Get the id from the last part of the url
        id = response.url.split("/")[-2]
        # We get the link of the video file
        js = response.selector.xpath(
            '//meta[@property="og:video"]/@content'
        ).extract()
        url = js[0]
        # We save the video
        yield scrapy.Request(
            url,
            meta={'id': id, 'extension': '.mp4'},
            callback=self.save_media
        )

    # Method for parsing a sidecar
    def parse_sideCar(self, response):
        # We get the json containing the photos's path
        js = response.selector.xpath(
            '//script[contains(., "window._sharedData")]/text()'
        ).extract()
        js = js[0].replace("window._sharedData = ", "")
        jscleaned = js[:-1]

        json_data = json.loads(jscleaned)
        json_data = json_data["entry_data"]["PostPage"][0]

        edges = json_data["graphql"]["shortcode_media"]["edge_sidecar_to_children"]["edges"]

        for edge in edges:
            url = edge["node"]["display_url"]
            id = edge["node"]['id']
            yield scrapy.Request(
                url,
                meta={'id': id, 'extension': '.jpg'},
                callback=self.save_media
            )

    # We grab the media with urllib
    def save_media(self, response):
        print("Downloading : " + response.url)
        fullfilename = os.path.join(self.savedir, response.meta['id'] + response.meta['extension'])
        urllib.request.urlretrieve(response.url, fullfilename)

    def getCurrentTime(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d_%H:%M")
