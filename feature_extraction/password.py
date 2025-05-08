from collections import Counter
import math
from typing import List, Tuple, Union
import pandas as pd
import hashlib
import requests
import zxcvbn


def shannon_entropy(password: str) -> float:
    """
    Calculate the Shannon entropy of a password.

    :param password: Password to calculate entropy for.
    :type password: str
    :return: Entropy of the password.
    :rtype: float
    """
    if not password:
        return 0
    count = Counter(password)
    length = len(password)
    probs = [freq / length for freq in count.values()]
    entropy = -sum(p * math.log2(p) for p in probs)
    return entropy


def password_strength(password: str) -> dict:
    """
    Check the strength of a password using the zxcvbn library.

    :param password: Password to check.
    :type password: str
    :return: Password strength information.
    :rtype: dict
    """
    result = zxcvbn.zxcvbn(password)
    filtered_result = {
        'password': password,
        # 'guesses': result['guesses'],
        'guesses_log10': result['guesses_log10'],
        'sequence': [
            {'token': seq['token'], 'pattern': seq['pattern']}
            for seq in result['sequence']
        ],
        'online_no_throttling_10_per_second_display': result['crack_times_display']['online_no_throttling_10_per_second'],
        'online_no_throttling_10_per_second_seconds': result['crack_times_seconds']['online_no_throttling_10_per_second'],
        'score': result['score']
    }

    return filtered_result


def check_pwned(passwords: Union[str, List[str]]) -> List[Tuple[str, int]]:
    """
    Check if a password has been leaked in a data breach using the HaveIBeenPwned Public API.

    :param passwords: Passwords to check.
    :type passwords: Union[str, List[str]]
    :raises ValueError: If passwords is empty.
    :return: List of tuples with password and count of leaks.
    :rtype: List[Tuple[str, int]]
    """
    if not passwords:
        raise ValueError("Los valores no se pueden dejar vacios")

    if not isinstance(passwords, list):
        passwords = [passwords]

    results = []
    for passphrase in passwords:
        # Envio de contraseñas hasheadas y no texto plano
        hashed_passphrase = hashlib.sha1(
            passphrase.encode()).hexdigest().upper()
        prefix, suffix = hashed_passphrase[:5], hashed_passphrase[5:]
        # Requests a la api
        url = f'https://api.pwnedpasswords.com/range/{prefix}'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for non-200 status codes
        except requests.HTTPError as e:
            print(f"Error al consultar la API: {e}")
            results.append((passphrase, 0))
            continue

        # Check if passphrase hash suffix exists in response
        for line in response.text.splitlines():
            suffix_, count = line.split(':')
            if suffix_ == suffix:
                results.append((passphrase, count))
                break

        # If suffix not found, add 0 count
        else:
            results.append((passphrase, 0))

    return results


def get_password(password: str, password_types: dict) -> pd.Series:
    """
    Get password information.

    :param password: Password to analyze.
    :type password: str
    :param password_types: Dictionary with password types.
    :type password_types: dict
    :return: Password information.
    :rtype: pd.Series
    """
    # Resultado de Password_update
    if "2024" in password or "2023" in password:
        actual = "actual"
    else:
        actual = "not actual"

    # Resultado de Password_type
    passwordtype = password_types.get(password, "personal password")

    # Resultado de Leaked_password
    pwned_results = check_pwned(password)
    pwned_count = pwned_results[0][1]  # Dato de Leaked passwords

    # Resultado de Password_strength, Guesses_discover, Cracking_time, Password_entropy
    strength_result = password_strength(password)
    entropy_estimate = shannon_entropy(password)

    # Resultado de hashes
    if password is None:  # Asegura manejar NoneTypes también.
        return [''] * 4
    md5 = hashlib.md5(password.encode()).hexdigest()
    sha256 = hashlib.sha256(password.encode()).hexdigest()
    sha512 = hashlib.sha512(password.encode()).hexdigest()
    sha1 = hashlib.sha1(password.encode()).hexdigest()

    data = [md5,
            sha256,
            sha512,
            sha1,
            actual,
            passwordtype,
            pwned_count,
            strength_result['score'],
            strength_result['guesses_log10'],
            strength_result['online_no_throttling_10_per_second_seconds'],
            entropy_estimate]

    index = ["md5",
             "sha256",
             "sha512",
             "sha1",
             "password_update",
             "password_type",
             "leaked_password",
             "password_strength",
             "guesses_discover",
             "cracking_time",
             "password_entropy"]

    results = pd.Series(data=data,
                        index=index)
    return results
