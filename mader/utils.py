import re


def sanitize_username(username: str) -> str:
    username = username.strip().lower()
    cleaned_username = re.sub(
        r'[^A-Za-z0-9 ]+', '', username
    )  # remove special characters
    cleaned_username = re.sub(
        r'\s+', ' ', cleaned_username
    )  # remove extra spaces
    return cleaned_username
