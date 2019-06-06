# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import urllib
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def download():
  url = "https://emojipedia.org"
  res = requests.get(url)
  soup = BeautifulSoup(res.text, 'html.parser')
  nav = soup.find("ul")
  nav_items = nav.find_all("li")

  pages = []

  for page in nav_items:
    pages.append(page.find("a")['href'])

  for page in pages:
    res = requests.get(url + page)
    soup = BeautifulSoup(res.text, 'html.parser')
    emojislist = soup.find("ul", class_="emoji-list")
    emojis = emojislist.find_all("li")

    for emoji in emojis:
      emojipage = emoji.find("a")['href']
      res = requests.get(url + emojipage)
      soup = BeautifulSoup(res.text, 'html.parser')

      try:
        shortcodesection = soup.find("ul", class_="shortcodes")
        shortcode = None

        if shortcodesection:
          shortcode = shortcodesection.find("li").text.replace(":", "")

        emojichar = soup.find("article").find("span", class_="emoji").text

        images = soup.find("section", class_="vendor-list").find_all("img")
        image = None

        for img in images:
          if "twemoji" in img['alt'].lower():
            image = img['src']
            break

        print(emojichar)
        if image and shortcode:
          try:
            urllib.urlretrieve(image, "downloads/%s~%s.%s" % (emojichar, shortcode, image.split(".")[-1]))
          except:
            urllib.request.urlretrieve(image, "downloads/%s~%s.%s" % (emojichar, shortcode, image.split(".")[-1]))
      except Exception as e:
        print(e)

if __name__ == '__main__':
  download()













  