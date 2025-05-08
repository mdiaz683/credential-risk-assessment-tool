import json
import random
import string
from pathlib import Path
import csv
import pandas as pd
import feature_extraction.user
import feature_extraction.file
import feature_extraction.channel
import feature_extraction.password


def password_generator(diccionario: dict) -> str:
    """
    Generates a random password.

    :param diccionario: Dictionary with words to use as passwords.
    :type diccionario: dict
    :return: Random password.
    :rtype: str
    """
    usar_diccionario = random.choice([True, False])
    if usar_diccionario and diccionario:
        return random.choice(diccionario)

    s1 = list(string.ascii_lowercase)
    s2 = list(string.ascii_uppercase)
    s3 = list(string.digits)
    s4 = list(string.punctuation)

    longitud = random.randint(4, 12)

    num_s1 = random.randint(1, longitud - 3)
    num_s2 = random.randint(1, longitud - num_s1 - 2)
    num_s3 = random.randint(1, longitud - num_s1 - num_s2 - 1)
    num_s4 = longitud - num_s1 - num_s2 - num_s3

    contrasena = (
        random.choices(s1, k=num_s1) +
        random.choices(s2, k=num_s2) +
        random.choices(s3, k=num_s3) +
        random.choices(s4, k=num_s4)
    )
    random.shuffle(contrasena)
    return ''.join(contrasena)


def load_channel_db(file_path: Path) -> dict:
    """
    Loads the channel database from a JSON file.

    :param file_path: Path to the JSON file with the channel database.
    :type file_path: Path
    :return: Dictionary with the channels and their type and privacy.
    :rtype: dict
    """
    channel_data = {}
    with open(file_path, "r", encoding="utf-8") as channel_f:
        channel_data = json.load(channel_f)
    channel_type = {}
    channel_priv = {}

    for chat_type, type in channel_data.items():
        for privacity_type, channels in type.items():
            for channel in channels:
                channel_type[channel] = chat_type
                channel_priv[channel] = privacity_type
    return channel_type, channel_priv


def load_file_db(file_path: Path):
    """
    Loads the file database from a JSON file.

    :param file_path: Path to the JSON file with the file database.
    :type file_path: Path
    :return: Dictionary with the files and their country.
    :rtype: dict
    """
    with open(file_path, "r") as files_f:
        files_data = json.load(files_f)
    return files_data


def load_user_db(file_path: Path) -> dict:
    """
    Loads the user database from a JSON file.

    :param file_path: Path to the JSON file with the user database.
    :type file_path: Path
    :return: Dictionary with the users and their group.
    :rtype: dict
    """
    with open(file_path, "r") as users_f:
        users_data = json.load(users_f)

    # Diccionario de búsqueda (user--> group; a@telebot.com=CEO)
    users_group = {}
    vip_users = {}
    users_status = {}
    for category, groups in users_data.items():
        for group_name, status in groups.items():
            for status_type, users in status.items():
                for user in users:
                    users_group[user] = group_name
                    vip_users[user] = category
                    users_status[user] = status_type
    return vip_users, users_group, users_status


def load_password_db(file_path: Path) -> dict:
    """
    Loads the password database from a JSON file.

    :param file_path: Path to the JSON file with the password database.
    :type file_path: Path
    :return: Dictionary with the passwords and their type.
    :rtype: dict
    """
    with open(file_path, "r") as pswd_f:
        pswd_data = json.load(pswd_f)
    pswd_type = {}
    for password_type, pswds in pswd_data.items():
        for pswd in pswds:
            pswd_type[pswd] = password_type

    return pswd_type


def gen_random_df(sample_data: dict, data_paths: dict, n_samples: int = 50) -> pd.DataFrame:
    """
    Generates a DataFrame with random data.

    :param sample_data: Dictionary with sample data.
    :type sample_data: dict
    :param data_paths: Dictionary with the paths to the data files.
    :type data_paths: dict
    :param n_samples: Number of samples to generate, defaults to 50
    :type n_samples: int, optional
    :return: DataFrame with random data.
    :rtype: pd.DataFrame
    """
    data = []
    sample_channel_df = pd.DataFrame(sample_data['channels'])
    sample_channel_names = sample_channel_df['CHANNEL_NAME'].tolist()
    for _ in range(n_samples):
        username = random.choice(sample_data['users'])
        password = password_generator(sample_data['diccionario'])
        channel = random.choice(sample_channel_names)
        file = random.choice(sample_data['file_name'])
        data.append([username, password, channel, file])
    df = pd.DataFrame(
        data, columns=['username', 'password', 'channel', 'file'])

    user_db = load_user_db(data_paths['user'])
    user_df = df['username'].apply(
        feature_extraction.user.get_user, args=(*user_db,))

    pwd_db = load_password_db(data_paths['password'])
    pwd_df = df['password'].apply(
        feature_extraction.password.get_password, args=(pwd_db,))

    files_data = load_file_db(data_paths['file'])

    df = pd.concat([df, user_df, pwd_df], axis=1)
    df = pd.merge(df, sample_channel_df, left_on='channel',
                  right_on='CHANNEL_NAME', how='left')
    df = df.drop_duplicates(
        subset=['username', 'password', 'channel', 'file']).reset_index(drop=True)
    df['country_file_name'] = df['file'].apply(
        lambda x: feature_extraction.file.get_country_file(x, files_data))
    df['leaked_password'] = df['leaked_password'].astype(int)
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace('-', '_')
    df.columns = df.columns.str.lower()
    return df


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    SAMPLES_DIR = BASE_DIR / "samples"

    with open(SAMPLES_DIR / "usernames.json", "r", encoding="utf-8") as users_file, \
            open(SAMPLES_DIR / "psw_dic.json", "r", encoding="utf-8") as diccionario_file, \
            open(SAMPLES_DIR / "channels.json", "r", encoding="utf-8") as channels_file, \
            open(SAMPLES_DIR / "file_name.json", "r", encoding="utf-8") as file_name_file:
        samples_data = {
            'users': json.load(users_file),
            'diccionario': json.load(diccionario_file),
            'channels': json.load(channels_file),
            'file_name': json.load(file_name_file)
        }

    data_paths = {
        'user': DATA_DIR / "user.json",
        'password': DATA_DIR / "password.json",
        'channel': DATA_DIR / "channel.json",
        'file': DATA_DIR / "file.json"
    }
    df = gen_random_df(samples_data, data_paths, n_samples=50)
    df.to_csv("output.csv", index=False)
