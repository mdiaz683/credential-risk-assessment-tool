from pathlib import Path
import json
import pandas as pd


# Función para obtener el nombre del país según el archivo y los datos del JSON
def get_country_file(file: str, files_data: dict) -> str:
    """
    Get the country name based on the file name and the JSON data.

    :param file: File name.
    :type file: str
    :param files_data: Dictionary with file data.
    :type files_data: dict
    :return: Country name.
    :rtype: str
    """
    for file_country, tokens in files_data.items():
        for token in tokens:
            if token.lower() in file.lower():  # discriminar mayus/minus
                return file_country
    return "Other"


if __name__ == "__main__":
    # Ruta del archivo CSV
    file_path = Path(__file__).parent.absolute() / "output.csv"
    df = pd.read_csv(file_path)

    # Ruta del archivo JSON
    BASE_DIR = Path(__file__).resolve().parent
    FILES_JSON = BASE_DIR / "file_det.json"

    # Cargar el archivo JSON
    with open(FILES_JSON, "r") as files_f:
        files_data = json.load(files_f)
