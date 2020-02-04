import os
import re
from datetime import datetime
from time import sleep

import requests
from dhooks import Embed, Webhook

auth_info = (os.environ["BOARD_ID"], os.environ["BOARD_PASS"])


def generate_embed(url):
    """
    URLのページを確認してEmbedに整形する
    """
    res = requests.get(url, auth=auth_info, timeout=10.0)
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
    # hook.send("@everyone")  # iPhoneで通知のバッチを付ける用

    # 記事一覧を取得
    year = now.year if (now := datetime.now()).month >= 4 else now.year - 1  # 年度
    url = f"{os.environ['BOARD_URL']}{year}/boards/new.html"
    try:
        res = requests.get(url, auth=auth_info, timeout=10.0)
    except Exception as e:
        hook.send(f"ERROR: {e}")
        return
    sleep(1)
    if (status := res.status_code) != requests.codes.ok:
        hook.send(f"Status code is {status}")
        return
    res.encoding = res.apparent_encoding
    all_articles = re.findall('<A HREF="(.+?)"', res.text)

    # 更新分の取得
    with open("latest", "r") as f:
        latest_article = f.read()
    updated_articles = all_articles[: all_articles.index(latest_article)]
    if not updated_articles:
        return
    try:
        for article in reversed(updated_articles):
            hook.send(embed=generate_embed(requests.compat.urljoin(url, article)))
            sleep(1)
    except Exception as e:
        hook.send(f"ERROR: {e}")
        return

    with open("latest", "w") as f:
        f.write(article)


if __name__ == "__main__":
    notify()
