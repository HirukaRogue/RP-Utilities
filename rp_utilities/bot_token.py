from dotenv import find_dotenv, get_key

TOKEN = get_key(find_dotenv(), "BOT_TOKEN")


def return_token() -> str | None:
    return TOKEN
