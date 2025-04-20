import codecs
import io
import os
import sys

import discord
from discord import app_commands
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

SERVER = {
    "jp": 1000,
    "Japan": 1000,
    "japan": 1000,
    "kr": 2000,
    "Korea": 2000,
    "korea": 2000,
    "Asia": 3000,
    "asia": 3000,
    "na": 5000,
    "NorthAmerica": 5000,
    "northamerica": 5000,
    "Europe": 5000,
    "europe": 5000,
    "Global": 6000,
    "global": 6000,
}

GVG_CLASSE_NAME = {
    1: "グランドマスター",
    2: "エキスパート",
    3: "エリート",
    4: "other",
}


@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")
    await tree.sync()  # スラッシュコマンドを同期


@tree.command(
    name="ranking",
    description="サーバーが属するグループのギルドランキングを表示",
)
@app_commands.describe(
    world_number="w99なら99のように入力してください",
    gvg_class="グループのクラスを選択してください",
    server="必要ならサーバー名を入力してください(例: jp, kr, asia, na, europe, global)",
)
@app_commands.choices(
    gvg_class=[
        app_commands.Choice(name="グランドマスター", value=1),
        app_commands.Choice(name="エキスパート", value=2),
        app_commands.Choice(name="エリート", value=3),
        app_commands.Choice(name="other", value=4),
    ]
)
async def ranking(
    interaction: discord.Interaction,
    world_number: int,
    gvg_class: app_commands.Choice[int],
    server: str = "jp",
):

    await interaction.response.send_message("処理中...")
    msg = await interaction.original_response()

    world_id = SERVER[server] + world_number
    sbody = mentemorimori_tool.output_bp_ranking(world_id, length=16 * gvg_class.value)

    sbody_split = sbody.splitlines()

    output = sbody_split[0] + "\n" + sbody_split[1] + f"({gvg_class.name})\n"
    output += "\n".join(
        sbody_split[2 + 16 * 2 * (gvg_class.value - 1) : 2 + 16 * 2 * gvg_class.value]
    )

    await msg.edit(content=output)


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
    world_id = SERVER[server] + world_number
    sbody = mentemorimori_tool.output_guild_info_detail(world_id, guild_id)

    await interaction.response.send_message(sbody)


@tree.command(name="sync_reload", description="スラッシュコマンドを手動で同期します")
async def sync_reload(interaction: discord.Interaction):
    await interaction.response.send_message("同期中...", ephemeral=True)
    msg = await interaction.original_response()

    synced = await tree.sync()
    await msg.edit(content=f"{len(synced)} 個のスラッシュコマンドを同期しました")


if APP_NAME == "testapp1_practice":

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
        interaction: discord.Interaction, sendtext: str = f"{APP_NAME} より心を込めて"
    ):

        name = interaction.user.name
        await interaction.response.send_message(
            f"{name} さん, こんにちは AAAAA\n" + str(sendtext)
        )


# ボットを起動
client.run(TOKEN)
