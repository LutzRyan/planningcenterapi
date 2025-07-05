import pandas as pd
import requests

from typing import TypedDict


class PlanningCenter(object):
    class ReponseData(TypedDict):
        data: list
        included: list

    __appId = "<YourAppIdHere>"
    __secret = "<YourSecretHere>"

    def __init__(self) -> None:
        self.baseUrl = f"https://api.planningcenteronline.com/"
        self.url = self.baseUrl
        self.parameters = {"per_page": 100}

    @property
    def __className(self) -> str:
        return self.__class__.__name__.lower()

    def __InjectUserandSecret(self, url: str) -> str:
        return url.replace("https://", f"https://{self.__appId}:{self.__secret}@")

    def Get(self) -> ReponseData:
        parameters = "&".join(
            [f"{key}={value}" for key, value in self.parameters.items()]
        )

        response = requests.get(self.__InjectUserandSecret(self.url) + "?" + parameters)
        data = response.json()["data"]

        included = response.json().get("included", [])

        totalCount = response.json()["meta"]["total_count"]
        retrievedCount = len(data)
        print(f"Retrieved {retrievedCount} of {totalCount} {self.__className}")

        while "next" in response.json()["links"]:
            nextUrl = self.__InjectUserandSecret(response.json()["links"]["next"])
            response = requests.get(nextUrl)
            data.extend(response.json()["data"])

            included.extend(response.json().get("included", []))

            totalCount = response.json()["meta"]["total_count"]
            retrievedCount = len(data)
            print(f"Retrieved {retrievedCount} of {totalCount} {self.__className}")

        return self.ReponseData(
            data=data,
            included=included,
        )
