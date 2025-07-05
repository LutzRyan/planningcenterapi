from datetime import datetime, timedelta
from .planningcenter import PlanningCenter
from typing import TypedDict


class Events(PlanningCenter):
    class Event(TypedDict):
        name: str
        id: int

    def __init__(self) -> None:
        super().__init__()
        self.url = self.baseUrl + "check-ins/v2/events"
        self.parameters.update({"order": "-created_at"})
        self.__originalParameters = self.parameters.copy()

    def GetEvent(self, id) -> Event:
        self.parameters = self.__originalParameters.copy()
        self.parameters.update(
            {
                "where[id]": id,
            }
        )

        responseData = self.Get()
        event = self.Event(
            name=responseData["data"][0]["attributes"]["name"],
            id=responseData["data"][0]["id"],
        )

        return event
