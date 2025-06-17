import codecs
import io
import sys


import discord
from discord import app_commands


def register_practice_commands(tree: app_commands.CommandTree):

    # コマンド: /sync_reload
    @tree.command(
        name="sync_reload", description="スラッシュコマンドを手動で同期します"
    )
    async def sync_reload(interaction: discord.Interaction):
        await interaction.response.send_message("同期中...", ephemeral=True)
        msg = await interaction.original_response()

        synced = await tree.sync()
        await msg.edit(content=f"{len(synced)} 個のスラッシュコマンドを同期しました")

    @tree.command(
        name="send_txt",
        description="テキストファイルを送信する",
    )
    async def send_txt(interaction: discord.Interaction):
        sendtext = "これはテストです。\nテキストファイルを送信できることを確かめるために作成されました。"

        sys.stdout = codecs.getwriter("utf_8")(sys.stdout)
        with io.StringIO(sendtext) as f:
            await interaction.channel.send(file=discord.File(f, "send.txt"))

    @tree.command(
        name="test",
        description="テスト用コマンド",
    )
    @app_commands.describe(
        text="テスト用のテキストを入力してください",
    )
    @app_commands.choices(
        text=[
            app_commands.Choice(name="テスト1", value=1),
            app_commands.Choice(name="テスト2", value=2),
            app_commands.Choice(name="テスト3", value=3),
        ]
    )
    async def test(
        interaction: discord.Interaction,
        text: app_commands.Choice[int],
        # text: app_commands.Choice[int] = app_commands.Choice(name="テスト1", value=1),
        # text: int = 1,
    ):
        await interaction.response.send_message(
            f"テスト用コマンドです\nあなたの選択: {text.name}（値: {text.value}）"
        )

        print(text, type(text))

    @tree.command(
        name="hello",
        description="挨拶する",
    )
    async def hello(
        interaction: discord.Interaction, sendtext: str = "よろしくお願いします"
    ):

        name = interaction.user.name
        await interaction.response.send_message(
            f"{name} さん, こんにちは\n" + str(sendtext)
        )
