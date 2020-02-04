import os
import re
from datetime import datetime

import requests
from dhooks import Embed, Webhook

auth_info = (os.environ["BOARD_ID"], os.environ["BOARD_PASS"])


def generate_embed(url):
    """
    URLのページを確認してEmbedに整形する
    """
    res = requests.get(url, auth=auth_info)
    res.encoding = res.apparent_encoding

    # 記事の本文
    body = re.search(
        "<!-- begin text -->\r\n(.+?)<!-- end text -->",
        res.text,
        flags=(re.MULTILINE | re.DOTALL),
    ).group(1)
    embed = Embed(description=body, color=0x7E6CA8)

    # 記事の詳細
    field = dict(re.findall("(.+?): (.+?)<BR>", res.text))
    if title := field.get("Subject"):
        embed.set_title(title=f":newspaper: {title}", url=url)
    if author := field.get("From"):
        embed.set_author(name=author.split("&")[0], icon_url=os.environ["FAVICON_URL"])
    if date := field.get("Date"):
        embed.set_footer(date)
    if reference := field.get("Reference"):
        link, text = re.search('<A HREF="(.+?)">(.+?)</A>', reference).groups()
        embed.add_field(
            name=":book: Reference",
            value=f"[{text}]({requests.compat.urljoin(url, link)})",
        )
    i = 1
    while True:
        if attach := field.get(f"Attach{i}"):
            link, text = re.search(
                '<A HREF="(.+?)" TARGET="attach">(.+?)</A>', attach
            ).groups()
            embed.add_field(
                name=f":file_folder: Attach{i}",
                value=f"[{text}]({requests.compat.urljoin(url, link)})",
            )
            i += 1
        else:
            break
    return embed


def notify():
    hook = Webhook(os.environ["DISCORD_WEBHOOK_URL"])
    hook.send(embed=generate_embed(os.environ["TEST_ARTICLE_URL"]))


if __name__ == "__main__":
    notify()
