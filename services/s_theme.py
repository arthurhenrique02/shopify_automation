import json
import os
import subprocess

from dotenv import load_dotenv

load_dotenv()


def get_theme_id(store_name: str, password: str) -> str:
    """
    Retrieves the theme ID from the Shopify store using the Shopify CLI.
    Args:
        store_name (str): The name of the Shopify store.
        password (str): The Theme access token.
    Returns:
        str: The theme ID if successful, None otherwise.
    """
    try:
        stdout, _ = subprocess.Popen(
            [
                f"{os.getenv('SHOPIFY_CLI_PATH')}",
                "theme",
                "list",
                "--store",
                store_name,
                "--json",
                "--password",
                password,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            universal_newlines=True,
        ).communicate()

        try:
            return json.loads(stdout)[0]["id"]
        except (json.JSONDecodeError, IndexError):
            print(
                "Failed to retrieve theme ID. Ensure the store URL and password are correct."
            )
            print("Output:", stdout)
            return None
    except subprocess.CalledProcessError as e:
        print("Error retrieving theme ID:", e)
        return None


def upload_shopify_theme(
    theme_id: str, folder_path: str, store_url: str, password: str
) -> bool:
    """
    Uploads a Shopify theme to the specified store.
    Args:
        theme_id (str): The ID of the theme to upload.
        folder_path (str): The path to the theme folder.
        store_url (str): The URL of the Shopify store.
        password (str): The Theme access token.
    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    if not theme_id or not folder_path or not store_url or not password:
        print("Missing required parameters for uploading theme.")
        return False

    try:
        subprocess.run(
            [
                f"{os.getenv('SHOPIFY_CLI_PATH')}",
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
                f"{theme_id}",
            ],
            encoding="utf-8",
            errors="replace",
            input="\n",
        )
    except subprocess.CalledProcessError as e:
        print(e)
        return False

    return True
