import codecs
import io
import os
import sys

import discord
from dotenv import load_dotenv

from mememori_tool import mentemorimori_tool

# .envファイルを読み込む
load_dotenv()
TOKEN = os.getenv("TOKEN")
APP_NAME = os.getenv("APP_NAME")


# botの設定
# intentsは、botにどのような権限を渡すかを設定するもの。defaultはすべてtrue
intents = discord.Intents.default()
client = discord.Client(intents=intents)

tree = discord.app_commands.CommandTree(client)

SERVERs = {
    "jp": 1000,
    "Japan": 1000,
    "japan": 1000,
    "Korea": 2000,
    "korea": 2000,
    "Asia": 3000,
    "asia": 3000,
    "NorthAmerica": 5000,
    "northamerica": 5000,
    "Europe": 5000,
    "europe": 5000,
    "Global": 6000,
    "global": 6000,
}


@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")
    await tree.sync()  # スラッシュコマンドを同期


@tree.command(
    name="hello",
    description="挨拶する",
)
async def hello(
    interaction: discord.Interaction, sendtext: str = f"{APP_NAME} より心を込めて"
):

    name = interaction.user.name
    await interaction.response.send_message(
        f"{name} さん, こんにちは\n" + str(sendtext)
    )


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
    name="ranking",
    description="サーバーが属するグループのギルドランキングを表示",
)
async def ranking(
    interaction: discord.Interaction,
    world_number: int,
    server: str = "jp",
    length: int = 16,
):
    world_id = SERVERs[server] + world_number
    sbody = mentemorimori_tool.output_bp_ranking(world_id, length=length)

    sbody_split = sbody.splitlines()
    output = []

    if length <= 16:
        output.append("----\n" + "\n".join(sbody_split))
    elif 17 < length and length <= 32:
        output.append("----\n" + "\n".join(sbody_split[:34]))
        output.append("----\n" + "\n".join(sbody_split[34:]))
    elif 32 < length and length <= 48:
        output.append("----\n" + "\n".join(sbody_split[:34]))
        output.append("----\n" + "\n".join(sbody_split[34:66]))
        output.append("----\n" + "\n".join(sbody_split[67:]))
    else:
        output.append("----\n" + "\n".join(sbody_split[:34]))
        output.append("----\n" + "\n".join(sbody_split[34:66]))
        output.append("----\n" + "\n".join(sbody_split[67:98]))
        output.append("----\n" + "\n".join(sbody_split[98:]))

    await interaction.response.send_message(output[0])
    if len(output) > 1:
        for i in output[1:]:
            await interaction.channel.send(i)


@tree.command(
    name="guildinfo",
    description="ギルドの詳細情報を表示",
)
async def guildinfo(
    interaction: discord.Interaction,
    world_number: int,
    guild_id: int,
    server: str = "jp",
):
    world_id = SERVERs[server] + world_number
    sbody = mentemorimori_tool.output_guild_info_detail(world_id, guild_id)

    await interaction.response.send_message(sbody)


# ボットを起動
client.run(TOKEN)
