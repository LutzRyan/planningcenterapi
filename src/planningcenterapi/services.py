import pandas as pd

from .planningcenter import PlanningCenter
from typing import TypedDict


class Teams(PlanningCenter):
    class TeamPerson(TypedDict):
        personId: int
        name: str
        teamName: str
        teamId: int
        lastName: str

    def __init__(self) -> None:
        super().__init__()
        self.url = self.baseUrl + "services/v2/teams"
        self.parameters.update({"order": "name"})
        self.__originalParameters = self.parameters.copy()

    def GetTeamsForPeople(self) -> list:
        self.parameters = self.__originalParameters.copy()
        self.parameters.update(
            {
                "include": "people,service_type",
                "where[service_type][name]": "Sunday Morning",
            }
        )

        responseData = self.Get()
        teams = []
        for teamData in responseData["data"]:
            if teamData["attributes"]["archived_at"] is not None:
                continue

            team = {
                "id": teamData["id"],
                "name": teamData["attributes"]["name"],
                "people": [],
            }

            for personData in teamData["relationships"]["people"]["data"]:
                team["people"].append(personData["id"])

            teams.append(team)

        people = []
        for personData in responseData["included"]:
            if personData["type"] != "Person":
                continue

            teamData = []
            for team in teams:
                if personData["id"] in team["people"]:
                    teamData.append((team["id"], team["name"]))

            lastName = personData["attributes"]["last_name"]
            name = (
                personData["attributes"]["first_name"]
                + " "
                + personData["attributes"]["last_name"]
            )
            for t in teamData:
                person = self.TeamPerson(
                    personId=personData["id"],
                    name=name,
                    teamId=t[0],
                    teamName=t[1],
                    lastName=lastName,
                )

                people.append(person)

        return people
