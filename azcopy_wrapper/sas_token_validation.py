import time
import datetime
from urllib.parse import parse_qs


def is_sas_token_session_expired(token: str) -> bool:
    """
    Checks if the SAS token is expired
    """
    parsed = parse_qs(token.lstrip("?"))

    # se is the query parameter for SessionExpiry field
    session_expiry = parsed.get("se")

    if session_expiry is None:
        raise Exception("Cannot find session expiry parameter in query")

    session_expiry_string = session_expiry[0]

    session_expiry_unix_timestamp = int(
        time.mktime(
            datetime.datetime.strptime(
                session_expiry_string, "%Y-%m-%dT%H:%M:%SZ"
            ).timetuple()
        )
    )

    current_timestamp = datetime.datetime.now(datetime.timezone.utc)

    current_unix_timestamp = int(time.mktime(current_timestamp.timetuple()))

    if current_unix_timestamp > session_expiry_unix_timestamp:
        return True
    else:
        return False
