import requests
import json
import os
from typing import Any, Optional

class EmbeddingModel:

    host = ""

    def __init__(self, model: str):
        self.model = model

    @classmethod
    def get_host(cls) -> Optional[str]:
        return cls.host

    def get_model(self) -> str:
        return self.model

    def get_envvar(self, name: str) -> str:
        val = os.getenv(name)
        if val is None:
            raise Exception(f"Environment variable {name} is not set")
        return val.strip()

    def call_server(self, url: str, token: Optional[str], payload: Any) -> Any:

        headers = {"Content-Type": "application/json"}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            error_message = response.text
            print(url + "\nreturned error\n" + error_message, flush=True)
            raise Exception("Model failed") from e
        except Exception as e:
            print(url + "\nfailed with exception\n" + str(e), flush=True)
            raise Exception("An error occurred") from e
        txt = response.text
        jsonz = {}
        try:
            jsonz = json.loads(txt)
        except BaseException as e:
            print(f"Error while trying to extract JSON\n{e}\nThe API answer is\n{txt}", flush=True)
            raise Exception(f"Error while trying to extract JSON from \"{txt}\", problem is: " + str(e)) from e
        return jsonz
