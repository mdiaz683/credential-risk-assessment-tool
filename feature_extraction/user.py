from pathlib import Path
import json
import pandas as pd


def get_user(username: str, vip_users: dict, user_groups: dict, user_status: dict):
    """
    Get user information from the user database.

    :param username: User name to search for.
    :type username: str
    :param vip_users: Dictionary with VIP users.
    :type vip_users: dict
    :param user_groups: Dictionary with user groups.
    :type user_groups: dict
    :param user_status: Dictionary with user status.
    :type user_status: dict
    :return: Series with user information.
    :rtype: pd.Series
    """
    return pd.Series({
        "vip_credentials": vip_users.get(username),
        "vip_group": user_groups.get(username),
        "user_status": user_status.get(username)
    })


if __name__ == "__main__":
    file_path = Path(__file__).parent.absolute() / "output.csv"
    df = pd.read_csv(file_path)

    # ruta del json
    BASE_DIR = Path(__file__).resolve().parent
    USERS_FILE = BASE_DIR / "user_det.json"

    # cargar el json
    with open(USERS_FILE, "r") as users_f:
        users_data = json.load(users_f)

    # Diccionario de búsqueda (user--> group; a@telebot.com=CEO)
    user_to_group = {}
    user_to_vip = {}
    user_to_status = {}
    for category, groups in users_data.items():
        for group_name, status in groups.items():
            for status_type, users in status.items():
                for user in users:
                    user_to_group[user] = group_name
                    user_to_vip[user] = category
                    user_to_status[user] = status_type

    df[["vip_credential", "vip_group", "user_status"]
       ] = df['username'].apply(get_user)
    print(df)
