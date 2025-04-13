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
        f"{name} さん, こんにちは AAAAA\n" + str(sendtext)
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

    await interaction.response.send_message("処理中...")
    msg = await interaction.original_response()

    world_id = SERVERs[server] + world_number
    sbody = mentemorimori_tool.output_bp_ranking(world_id)
    # print(sbody)

    sbody_split = sbody.splitlines()

    output = []
    output.append("\n".join(sbody_split[: 2 + 16 * 2]))
    # print(output[0])
    await msg.edit(content=output[0])

    for i in range(1, 4):
        if 16 * i < length:
            output.append("\n".join(sbody_split[2 + 16 * 2 * i : 2 + 16 * 2 * (i + 1)]))
            # print(output[i])
            await interaction.channel.send(output[i])


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


@tree.command(name="sync_reload", description="スラッシュコマンドを手動で同期します")
async def sync_reload(interaction: discord.Interaction):
    await interaction.response.send_message("同期中...", ephemeral=True)
    msg = await interaction.original_response()

    synced = await tree.sync()
    await msg.edit(content=f"{len(synced)} 個のスラッシュコマンドを同期しました")


# ボットを起動
client.run(TOKEN)
