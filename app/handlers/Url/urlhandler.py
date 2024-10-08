from ...core.database import urls_collection
from pydantic import HttpUrl
from ..exception import ErrorHandler
import secrets
import string
from ...utils.envutils import Environment
import socket

env = Environment()


class HandleUrl:
    @staticmethod
    def generate_unique_string():
        alphabet = string.ascii_letters + string.digits
        shorted_string = ''.join(secrets.choice(alphabet) for _ in range(8))
        return shorted_string

    @staticmethod
    async def HandleUrlShortening(url: HttpUrl):
        """
        Shorten the long URL to a short URL.
        """
        try:
            domain = url.host
            try:
                # Perform DNS resolution
                socket.gethostbyname(domain)
            except socket.gaierror:
                return ErrorHandler.NotFound("Domain does not exist or is unreachable.")

            # Generate unique string
            unique_strings = HandleUrl.generate_unique_string()
            new_url = await urls_collection.insert_one({"long_url": str(url), "short_url": f"{unique_strings}"})
            return {"short_url": f"{env.DOMAIN}{unique_strings}"}

        except Exception as e:
            return ErrorHandler.Error(str(e))


    @staticmethod
    async def HandleUrlRedirection(unique_string: str):
        """
        Redirect to the long url
        """
        try:
            url = await urls_collection.find_one({"short_url": unique_string})
            if url:
                return {"long_url": url["long_url"]}
            return ErrorHandler.NotFound("Url does not exists or is invaild")
        except Exception as e:
            return ErrorHandler.Error(str(e))
