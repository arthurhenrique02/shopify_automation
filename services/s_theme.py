import subprocess
import typing


def upload_shopify_theme(folder_path: str, store_url: str, password: str):
    try:
        subprocess.Popen(
            [
                "C:/Users/arthu/AppData/Roaming/npm/shopify.cmd",
                "theme",
                "push",
                "--path",
                str(folder_path),
                "--store",
                store_url,
                "--publish",
                "--json",
                "--allow-live",
                "--force",
                "--ignore",
                "none",
                "--password",
                f"{password}",
                "--theme",
                "Dawn",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as e:
        print(e)


# TODO CHANGE COLLECTION LIST DATA
def change_collection_data(collections: typing.List[dict]):
    """
        CHANGE THESE LINES IN SETTINGS_DATA.JSON
    "collection_list_AHQMEf":{"type":"collection-list","blocks":{"featured_collection_GJWefx":{"type":"featured_collection","settings":{"collection":""}},"featured_collection_KLhC6x":{"type":"featured_collection","settings":{"collection":""}},"featured_collection_LnT4kD":{"type":"featured_collection","settings":{"collection":""}},"featured_collection_jxHkzt":{"type":"featured_collection","settings":{"collection":""}}},"block_order":["featured_collection_GJWefx","featured_collection_KLhC6x","featured_collection_LnT4kD","featured_collection_jxHkzt"],"name":"Collection list","settings":{"layout":"container","title":"Lista de colecciones","grid":4}}}
    """
    ...
