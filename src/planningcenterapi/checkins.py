from datetime import datetime, timedelta
from .planningcenter import PlanningCenter
from .events import Events
from typing import TypedDict


class CheckIns(PlanningCenter):
    class CheckIn(TypedDict):
        firstName: str
        lastName: str
        personId: int
        checkInDate: str
        checkInTime: str
        eventPeriodId: int

    def __init__(self) -> None:
        super().__init__()
        self.url = self.baseUrl + "check-ins/v2/check_ins"
        self.parameters.update(
            {"include": "event_period,event", "order": "-created_at"}
        )
        self.__originalParameters = self.parameters.copy()

    def __AddEventPeriods(self, checkIns: list, eventPeriods: list) -> list:
        if not eventPeriods:
            return checkIns

        eventPeriodsDict = {}
        for eventPeriod in eventPeriods:
            eventPeriodId = eventPeriod["id"]
            eventPeriodDate = eventPeriod["attributes"]["starts_at"][:10]
            eventPeriodTime = eventPeriod["attributes"]["starts_at"][11:19]

            eventPeriodsDict[eventPeriodId] = {
                "eventPeriodDate": eventPeriodDate,
                "eventPeriodTime": eventPeriodTime,
            }

        for checkIn in checkIns:
            eventPeriodId = checkIn["eventPeriodId"]
            eventPeriod = eventPeriodsDict.get(eventPeriodId, {})
            checkIn["checkInDate"] = eventPeriod.get("eventPeriodDate", "")
            checkIn["checkInTime"] = eventPeriod.get("eventPeriodTime", "")

        return checkIns

    def GetCheckIns(self, weeks) -> list:
        self.parameters = self.__originalParameters.copy()
        self.parameters.update(
            {
                "where[created_at][gte]": datetime.now() - timedelta(weeks=weeks),
            }
        )

        responseData = self.Get()
        checkIns = []
        events = []
        sundayWorshipEventId = 0
        eventApi = Events()
        for checkInData in responseData["data"]:
            eventId = checkInData["relationships"]["event"]["data"]["id"]
            if eventId not in [event["id"] for event in events]:
                event = eventApi.GetEvent(eventId)
                if event["name"] == "Sunday Worship":
                    sundayWorshipEventId = eventId

                events.append(event)

            if eventId != sundayWorshipEventId:
                continue

            # if not checkInData["relationships"]["person"]["data"]:  # Skip if no person
            #     continue
            
            checkIn = self.CheckIn(
                firstName=checkInData["attributes"]["first_name"],
                lastName=checkInData["attributes"]["last_name"],
                personId=checkInData["relationships"]["person"]["data"]["id"],
                eventPeriodId=checkInData["relationships"]["event_period"]["data"][
                    "id"
                ],
            )
            checkIns.append(checkIn)

        eventPeriods = [
            ep for ep in responseData["included"] if ep["type"] == "EventPeriod"
        ]
        checkIns = self.__AddEventPeriods(checkIns, eventPeriods)

        return checkIns

