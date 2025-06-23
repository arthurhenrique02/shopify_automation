import os
import subprocess


def upload_shopify_theme(zip_path: str, store_url: str = os.getenv("SHOP_NAME")):
    # with tempfile.TemporaryDirectory(suffix="_shopify_theme") as temp_dir:
    #     with zipfile.ZipFile(zip_path, "r") as zip_ref:
    #         zip_ref.extractall(temp_dir)

    #     theme_folders = [
    #         f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))
    #     ]
    #     if not temp_dir or not theme_folders:
    #         raise Exception("No theme folder found in zip.")
    #     print(temp_dir, theme_folders)

    #     print("======================")
    #     print(os.listdir(temp_dir))
    #     print("======================")
    #     subprocess.run(["cmd", "/c", "dir", temp_dir])  # Windows equivalent of 'ls -la'
    try:
        result = subprocess.run(
            [
                "C:/Users/arthu/AppData/Roaming/npm/shopify.cmd",
                "theme",
                "push",
                "--path",
                str(zip_path),
                "--store",
                store_url,
                "--publish",
                "--allow-live",
                "--json",
            ],
            check=True,
            capture_output=True,
        )
        print(result.stdout.decode("utf-8"))
        print("passei")
    except subprocess.CalledProcessError as e:
        print(e)
