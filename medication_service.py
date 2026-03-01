from db import database
from models import Medication
from bson.objectid import ObjectId

collection = database.get_collection("medications")


def add_medication(name, dosage, time, frequency, start_date, end_date):
    medication = Medication(name, dosage, time, frequency, start_date, end_date)
    collection.insert_one(medication.to_dict())


def get_all_medications():
    return list(collection.find())


def delete_medication(med_id):
    collection.delete_one({"_id": ObjectId(med_id)})