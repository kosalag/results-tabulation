import csv

from app import db
from orm.entities import *
from orm.entities.Submission.Report import Report_PRE_41, Report_PRE_30_PD, Report_PRE_30_ED

from orm.enums import ReportCodeEnum, AreaTypeEnum, TallySheetCodeEnum
from api.TallySheetVersionApi import TallySheetVersionPRE41Api

from sqlalchemy.sql import func

# db.engine.execute("create database election")


# Create the database
db.create_all()

election = Election.create(electionName="Test Election")

data_stores = {}

csv_dir = "./sample-data"


def get_data_store(data_store_key):
    if data_store_key not in data_stores:
        data_stores[data_store_key] = {}

    return data_stores[data_store_key]


def get_object_from_data_store(data_key, data_store_key):
    data_store = get_data_store(data_store_key)
    if data_key in data_store:
        return data_store[data_key]
    else:
        return None


def set_object_to_data_store(data_key, data_store_key, obj):
    data_store = get_data_store(data_store_key)
    data_store[data_key] = obj


def get_object(row, row_key):
    cell = row[row_key]
    data_key = cell
    data_store_key = row_key

    obj = get_object_from_data_store(data_key, data_store_key)

    if obj is None:
        if data_store_key == "Ballot":
            obj = Ballot.create(ballotId=cell, electionId=election.electionId)
        elif data_store_key == "Ballot Box":
            obj = BallotBox.create(ballotBoxId=cell, electionId=election.electionId)
        elif data_store_key == "Party":
            obj = Party.create(partyName=cell, partySymbol=row["Party Symbol"])
        elif data_store_key == "Candidate":
            obj = Candidate.create(candidateName=cell)
        elif data_store_key == "Country":
            obj = Country.create(cell, electionId=election.electionId)
        elif data_store_key == "Electoral District":
            obj = ElectoralDistrict.create(cell, electionId=election.electionId)
        elif data_store_key == "Polling Division":
            obj = PollingDivision.create(cell, electionId=election.electionId)
        elif data_store_key == "Polling District":
            obj = PollingDistrict.create(cell, electionId=election.electionId)
        elif data_store_key == "Election Commission":
            obj = ElectionCommission.create(cell, electionId=election.electionId)
        elif data_store_key == "District Centre":
            obj = DistrictCentre.create(cell, electionId=election.electionId)
        elif data_store_key == "Counting Centre":
            obj = CountingCentre.create(cell, electionId=election.electionId)
        elif data_store_key == "Polling Station":
            obj = PollingStation.create(cell, electionId=election.electionId)
        else:
            print("-------------  Not supported yet : ", data_store_key)

        set_object_to_data_store(data_key, data_store_key, obj)

    return obj


def get_rows_from_csv(csv_path):
    with open("%s/%s" % (csv_dir, csv_path), 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        rows = list(reader)

    return rows


for row in get_rows_from_csv('data.csv'):
    country = get_object({"Country": "Sri Lanka"}, "Country")
    electoralDistrict = get_object(row, "Electoral District")
    pollingDivision = get_object(row, "Polling Division")
    pollingDistrict = get_object(row, "Polling District")
    electionCommission = get_object({"Election Commission": "Sri Lanka Election Commission"}, "Election Commission")
    districtCentre = get_object(row, "District Centre")
    countingCentre = get_object(row, "Counting Centre")
    pollingStation = get_object(row, "Polling Station")

    country.add_child(electoralDistrict.areaId)
    electoralDistrict.add_child(pollingDivision.areaId)
    pollingDivision.add_child(pollingDistrict.areaId)
    pollingDistrict.add_child(pollingStation.areaId)
    electionCommission.add_child(districtCentre.areaId)
    districtCentre.add_child(countingCentre.areaId)
    countingCentre.add_child(pollingStation.areaId)

for row in get_rows_from_csv('parties.csv'):
    party = get_object(row, "Party")
    election.add_party(partyId=party.partyId)

for row in get_rows_from_csv('ballots.csv'):
    ballot = get_object(row, "Ballot")

for row in get_rows_from_csv('ballot-boxes.csv'):
    ballot = get_object(row, "Ballot Box")

for row in get_rows_from_csv('party-candidate.csv'):
    party = get_object(row, "Party")
    candidate = get_object(row, "Candidate")

    election.add_candidate(candidateId=candidate.candidateId, partyId=party.partyId)