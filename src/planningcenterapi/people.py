from datetime import datetime, timedelta
from .planningcenter import PlanningCenter
from typing import TypedDict


class People(PlanningCenter):
    class PersonData(TypedDict):
        id: str
        name: str
        fieldData: list
        lastName: str
        membership: str
        # shepherdingElder: str

    def __init__(self) -> None:
        super().__init__()
        self.url = self.baseUrl + "people/v2/people"
        self.parameters.update({"include": "field_data", "order": "-created_at"})
        self.__originalParameters = self.parameters.copy()
        self.__fieldDefinitions = []

    @property
    def fieldDefinitions(self) -> list:
        if not self.__fieldDefinitions:
            fieldDefinition = FieldDefinition()
            self.__fieldDefinitions = fieldDefinition.GetFieldDefinitions()

        return self.__fieldDefinitions

    def __AddFieldData(self, people: list, fieldData: list, fieldDataName: str) -> list:
        if not fieldData:
            return people

        fieldId = next(
            fieldDefinition["id"]
            for fieldDefinition in self.fieldDefinitions
            if fieldDefinition["name"] == fieldDataName
        )

        fieldDataDict = {}
        for fieldDatum in fieldData:
            if fieldDatum["type"] != "FieldDatum":
                continue

            fieldDefinition = fieldDatum["relationships"]["field_definition"]
            fieldDefinitionId = fieldDefinition["data"]["id"]

            if fieldDefinitionId != fieldId:
                continue

            fieldDatumId = fieldDatum["id"]
            fieldDataDict[fieldDatumId] = fieldDatum["attributes"]["value"]

        fieldDataName = fieldDataName[0].lower() + fieldDataName[1:].replace(" ", "")
        for person in people:
            for personFieldData in person["fieldData"]:
                fieldData = fieldDataDict.get(personFieldData["id"], {})
                if fieldData:
                    if person.get(fieldDataName) is not None:
                        person[fieldDataName] = person[fieldDataName] + ", " + fieldData
                    else:
                        person[fieldDataName] = fieldData

        return people

    def __AddShepherdingElder(self, people: list, fieldData: list) -> list:
        if not fieldData:
            return people

        shepherdingElderFieldId = next(
            fieldDefinition["id"]
            for fieldDefinition in self.fieldDefinitions
            if fieldDefinition["name"] == "Shepherding Elder"
        )

        fieldDataDict = {}
        for fieldDatum in fieldData:
            if fieldDatum["type"] != "FieldDatum":
                continue

            fieldDefinition = fieldDatum["relationships"]["field_definition"]
            fieldDefinitionId = fieldDefinition["data"]["id"]

            if fieldDefinitionId != shepherdingElderFieldId:
                continue

            fieldDatumId = fieldDatum["id"]
            fieldDataDict[fieldDatumId] = fieldDatum["attributes"]["value"]

        for person in people:
            for personFieldData in person["fieldData"]:
                fieldData = fieldDataDict.get(personFieldData["id"], {})
                if fieldData:
                    person["shepherdingElder"] = fieldData
                    break

        return people

    def GetActivePeople(self) -> list:
        self.parameters = self.__originalParameters.copy()
        self.parameters.update({"where[status]": "active"})

        responseData = self.Get()
        people = []
        for persondata in responseData["data"]:
            lastName = persondata["attributes"]["last_name"]
            name = (
                persondata["attributes"]["first_name"]
                + " "
                + persondata["attributes"]["last_name"]
            )
            fieldData = persondata["relationships"]["field_data"]["data"]
            person = self.PersonData(
                id=persondata["id"],
                name=name,
                fieldData=fieldData,
                membership=persondata["attributes"]["membership"],
            )
            people.append(person)

        people = self.__AddShepherdingElder(people, responseData["included"])

        return people

    # def GetMembers(self) -> list:
    #     self.parameters = self.__originalParameters.copy()
    #     self.parameters.update({"where[membership]": "Member"})

    #     responseData = self.Get()
    #     people = []
    #     for persondata in responseData["data"]:
    #         lastName = persondata["attributes"]["last_name"]
    #         name = (
    #             persondata["attributes"]["first_name"]
    #             + " "
    #             + persondata["attributes"]["last_name"]
    #         )
    #         fieldData = persondata["relationships"]["field_data"]["data"]
    #         person = self.PersonData(
    #             id=persondata["id"],
    #             name=name,
    #             fieldData=fieldData,
    #         )
    #         people.append(person)

    #     people = self.__AddShepherdingElder(people, responseData["included"])

    #     return people

    def GetRecentInactivePeople(self, weeksInactive: int) -> list:
        self.parameters = self.__originalParameters.copy()
        self.parameters.update(
            {
                "where[status]": "inactive",
                "where[updated_at][gte]": datetime.now()
                - timedelta(weeks=weeksInactive),
            }
        )

        responseData = self.Get()
        people = []
        for persondata in responseData["data"]:
            lastName = persondata["attributes"]["last_name"]
            name = (
                persondata["attributes"]["first_name"]
                + " "
                + persondata["attributes"]["last_name"]
            )
            fieldData = persondata["relationships"]["field_data"]["data"]
            person = self.PersonData(
                id=persondata["id"],
                name=name,
                fieldData=fieldData,
                membership=persondata["attributes"]["membership"],
                # lastName=lastName,
            )
            people.append(person)

        people = self.__AddShepherdingElder(people, responseData["included"])

        return people

    def GetPeople(self, where: dict) -> list:
        self.parameters = self.__originalParameters.copy()

        for key, value in where.items():
            self.parameters.update({f"where[{key}]": value})

        responseData = self.Get()
        people = []
        for persondata in responseData["data"]:
            lastName = persondata["attributes"]["last_name"]
            name = (
                persondata["attributes"]["first_name"]
                + " "
                + persondata["attributes"]["last_name"]
            )
            fieldData = persondata["relationships"]["field_data"]["data"]
            person = self.PersonData(
                id=persondata["id"],
                name=name,
                fieldData=fieldData,
                lastName=lastName,
            )
            people.append(person)

        people = self.__AddFieldData(
            people, responseData["included"], "Shepherding Elder"
        )
        people = self.__AddFieldData(
            people, responseData["included"], "Weekly Serving Areas"
        )

        return people


class FieldDefinition(PlanningCenter):
    class FieldDefinitionData(TypedDict):
        id: str
        name: str

    def __init__(self) -> None:
        super().__init__()
        self.url = self.baseUrl + "people/v2/field_definitions"
        self.parameters.update({"per_page": 100})
        self.__originalParameters = self.parameters.copy()

    def GetFieldDefinitions(self) -> list:
        self.parameters = self.__originalParameters.copy()

        responseData = self.Get()
        fieldDefinitions = [
            self.FieldDefinitionData(id=field["id"], name=field["attributes"]["name"])
            for field in responseData["data"]
        ]

        return fieldDefinitions
