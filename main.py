import os

import discord
from discord import app_commands
from dotenv import load_dotenv

from mememori_tool import guild_ranking

# .envファイルを読み込む
load_dotenv()
TOKEN = os.getenv("TOKEN")


# botの設定
# intentsは、botにどのような権限を渡すかを設定するもの。defaultはすべてtrue
intents = discord.Intents.default()
client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

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
async def hello(interaction: discord.Interaction, sendtext: str = "by discord.py"):
    await interaction.response.send_message("hello world, " + str(sendtext))


@tree.command(
    name="ranking",
    description="サーバーが属するグループのギルドランキングを表示",
)
async def ranking(
    interaction: discord.Interaction, world_number: int, server: str = "jp"
):
    world_id = SERVERs[server] + world_number
    # print(world_id, server, world_number)
    sbody = guild_ranking.get_sorted_bp(world_id)

    # sbody = str(world_number) + server

    await interaction.response.send_message(sbody)


# ボットを起動
client.run(TOKEN)
