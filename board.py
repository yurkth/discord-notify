import os

from dhooks import Embed, Webhook


def notify():
    hook = Webhook(os.environ["DISCORD_WEBHOOK_URL"])

    embed = Embed(description="本文", color=0x7E6CA8)
    embed.set_title(title=":newspaper: Subject", url="https://example.com")
    embed.set_author(name="From", icon_url=os.environ["ICON_URL"])
    embed.set_footer("2020/01/24 16:29:54")
    embed.add_field(name=":book: Reference", value="[リンク](https://example.com)")
    embed.add_field(name=":file_folder: Attach", value="[リンク](https://example.com)")

    hook.send(embed=embed)


if __name__ == "__main__":
    notify()
