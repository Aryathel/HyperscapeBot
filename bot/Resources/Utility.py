"""Resource | Utility Fcuntions

This file hosts classes/functions which are used regularly throughout
the program. More details provided for each.
"""
import discord
import datetime

class EmbedUtil:
    def __init__(self, bot):
        self.embed_color = bot.embed_color
        self.footer = bot.footer
        self.footer_image = bot.footer_image
        self.timestamp = bot.embed_ts
        self.show_author = bot.show_command_author

    def get_embed(self, title = None, desc = None, fields = None, ts = False, author = None, thumbnail = None, image = None, author_url = None):
        """Function | Create Embedded Message

        This function reads the default embed settings from the bot
        attributes, then creates an embedded message to the specifications
        of the input.
        """
        embed = discord.Embed(
            title = title,
            description = desc,
            color = self.embed_color
        )
        embed.set_footer(
            text = self.footer,
            icon_url = self.footer_image
        )
        if ts:
            embed.timestamp = self.timestamp()
        if self.show_author == True and author:
            embed.set_author(
                name = author.name,
                icon_url = author.avatar_url
            )
        if type(author) == str and author_url:
            embed.set_author(
                name = author,
                url = author_url
            )
        if author_url:
            embed.url = author_url
        if fields:
            for field in fields:
                embed.add_field(
                    name = field['name'],
                    value = field['value'],
                    inline = field['inline']
                )
        if thumbnail:
            embed.set_thumbnail(
                url = thumbnail
            )
        if image:
            embed.set_image(
                url = image
            )
        return embed

    def update_embed(self, embed, title = None, desc = None, ts = False, author = None, thumbnail = None, image = None):
        """Function | Modify Embedded Message

        This function takes in an embedded message and modifies it
        based on inputs.
        """
        if title:
            embed.title = title
        if desc:
            embed.description = desc
        if ts == True:
            embed.timestamp = self.timestamp()
        if author:
            embed.set_author(
                name = author.name,
                icon_url = author.avatar_url
            )
        if thumbnail:
            embed.set_thumbnail(
                url = thumbnail
            )
        if image:
            embed.set_image(
                url = image
            )
        return embed
