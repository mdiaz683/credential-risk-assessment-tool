from typing import Union
import streamlit as st
from streamlit_option_menu import option_menu
from pathlib import Path
import json
from randomizer import gen_random_df
import pickle
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.kernel_ridge import KernelRidge
import pandas as pd
import os
from streamlit_jupyter import StreamlitPatcher, tqdm
from settings import (
    BASE_DIR,
    SAMPLES_DIR,
    DATA_DIR
)

# register streamlit with jupyter-compatible wrappers


def cvss_score(x: Union[int, float]) -> str:
    """
    CVSS v3 severity score based on the risk value predicted by the model.

    :param x: Risk value
    :type x: Union[int, float]
    :return: Severity
    :rtype: str
    """
    if x == 0:
        return 'None'
    elif x < 40:
        return 'Low'
    elif x < 70:
        return 'Medium'
    elif x < 90:
        return 'High'
    else:
        return 'Critical'


class DropColumns(BaseEstimator, TransformerMixin):
    """
    Drop columns from a DataFrame

    :param BaseEstimator: Base class for all estimators in scikit-learn
    :type BaseEstimator: BaseEstimator
    :param TransformerMixin: Mixin class for all transformers in scikit-learn
    :type TransformerMixin: TransformerMixin
    """

    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.drop(columns=self.columns)


st.set_page_config(layout="wide",
                   page_title="Credential Risk Assessment Tool",
                   page_icon=":material/password:",
                   menu_items={
                       "Get Help": "mailto:victorluque341@gmail.com",
                       "Report a bug": "mailto:victorluque341@gmail.com",
                       "About": """
                                Author: María Diaz Alba\
                                
                                Developed by: [Victor Luque Martín](https://www.linkedin.com/in/victor-luque-martin/)\
                                
                                Version: 1.0.0"""
                   })


with open(SAMPLES_DIR / "usernames.json", "r", encoding="utf-8") as users_file, \
        open(SAMPLES_DIR / "password.json", "r", encoding="utf-8") as diccionario_file, \
        open(SAMPLES_DIR / "channels.json", "r", encoding="utf-8") as channels_file, \
        open(SAMPLES_DIR / "file_name.json", "r", encoding="utf-8") as file_name_file, \
        open(BASE_DIR / "pipeline.pkl", "rb") as model_file:
    samples_data = {
        'users': json.load(users_file),
        'diccionario': json.load(diccionario_file),
        'channels': json.load(channels_file),
        'file_name': json.load(file_name_file)
    }
    pipeline = pickle.load(model_file)

data_paths = {
    'user': DATA_DIR / "user.json",
    'password': DATA_DIR / "password.json",
    'channel': DATA_DIR / "channel.json",
    'file': DATA_DIR / "file.json"
}


def load_home():
    """
    Home page
    """
    st.markdown("""
        # About Dataset
        ## Risk Credential Assessment Dataset
        
        ### Dataset Description
        This dataset contains the necessary data about leaked credentials in Telegram to predict their degree of criticality. The data is based on the characteristics that, in the context of Telegram data leaks, refer to the risk that a credential leaked by a group or channel may present. These characteristics refer to the user, his password, the group / channel through which it was sent and the file in which it was sent. The datatset is ideal for analysts using the Telegram bot to detect credentials in real time, efficiently identifying the most critical alerts and performing an objective and rigorous analysis.
        
        ### Features
        * **Username**: Unique name representing the username of each leaked credential
        * **VIP_credentials**: The type of user by the work position, which can be VIP or not VIP
        * **VIP_group**: The type of VIP user group, which can be "ceo", "directiva", "ciber", "otros"
        * **User_status**: The status of the user, which can be active or inactive
        * **Password**: Unique name representing the password of each leaked credential
        * **Password_update**: Indicates the currentness of the password, if it contains "2024" or not
        * **Password_type**: The type of a password, which can be "Password for change", "Default password" or "Personal password"
        * **Leaked_password**: The number of times a password has been compromised according to HaveIBeenPwned's source
        * **Guesses_discover**: The number of attempts it takes to guess the password by a brute force attack
        * **Cracking_time**: The estimated time to guess the password
        * **Password_strength**: The score in a scale from 0 to 4 that represents the strength of a password
        * **Password_entropy**: The number of bits that represents the uncertainty of a password
        * **SHA1** password: Unique name representing the hash of the password with the SHA1 algorithm
        * **SHA256** password: Unique name representing the hash of the password with the SHA256 algorithm
        * **SHA512** password: Unique name representing the hash of the password with the SHA512 algorithm
        * **MD5** password: Unique name representing the hash of the password with the MD5 algorithm
        * **Channel_name**: Unique name representing the channel through which the credential was sent
        * **Chat_type**: The type of chat, which can be group or channel
        * **Channel_privacity**: The type of privacity of a channel or group, which can be public or private
        * **Subscribers**: The number of channel or group subscribers
        * **Engagement_rate**: The ratio of the average number of views per post to the number of subscribers
        * **Mentions**: The total count of channel mentions over its entire existence
        * **Posts_day**: The average number of posts per day for the last 30 days
        * **Reposts**: The average number of shares per post over the past 30 days
        * **Channel_country**: The country where the channel is from
        * **File**: Unique name representing the file name that contains the leaked credential
        * **Country_file_name**: Represents if the file name contains "Spain" or similar, "Europe" or similar, or neither
        * **Results_file**: The amount of results in the analyzed file
        * **TOTAL**: Target to predict, the numerical value representing the credential risk
        ### Source
        The data is sourced from the metadata "username", "password", "channel" and "file" of the credentials of the alerts generated by the Telegram bot.
        ### Applications
        * Risk management and analytical optimization
        * Machine learning and AI-driven prediction models
        * Academic research and projects
        """)


def load_generate_random_data():
    """
    Generate random data page
    """
    st.title("Generate Random Data")
    n_samples = st.number_input(
        "Number of samples", min_value=1, max_value=100, value=50, step=1)
    if st.button("Generate"):
        with st.spinner("Generating random data..."):
            df = gen_random_df(samples_data, data_paths, n_samples=n_samples)
        st.write(df)
        st.download_button("Download", df.to_json(
            orient="records"), f"random_data_{n_samples}.json", "application/json")


def load_try_model():
    """
    Try the model page
    """
    st.title("Want to make some predictions?")
    file = st.file_uploader("Upload a file", type=['json'])
    if file:
        df = pd.read_json(file)
        predictions = pipeline.predict(df)
        predictions = predictions * 100
        predictions = predictions.astype(int)
        results = pd.concat([df, pd.Series(predictions, name="risk")], axis=1)
        results['severity'] = results['risk'].apply(cvss_score)
        st.write(
            results[['username', 'password', 'channel', 'file', 'risk', 'severity']])
        st.download_button("Download", results.to_json(
            orient="records"), "predictions.json", "application/json")


def load_about():
    """
    About page
    """
    st.title("About")


with st.sidebar:
    elements = [
        "Home:house",
        "Generate Data:database-gear",
        "Make Magic:magic",
        # "About:info-circle"
    ]
    selected = option_menu("Main Menu",
                           [x.split(":")[0] for x in elements],
                           icons=[x.split(":")[1] for x in elements])

match selected:
    case "Home":
        load_home()
    case "Generate Data":
        load_generate_random_data()
    case "Make Magic":
        load_try_model()
    case _:
        st.write("Select an option from the sidebar")
    # case "About":
    #    load_about()
