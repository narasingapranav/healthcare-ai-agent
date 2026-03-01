from db import collection
from datetime import datetime

def add_medication(name, dosage, time, frequency, start_date, end_date):
    data = {
        "name": name,
        "dosage": dosage,
        "time": time,
        "frequency": frequency,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "created_at": datetime.now()
    }
    collection.insert_one(data)

def get_all_medications():
    return list(collection.find())

def delete_medication(med_id):
    from bson.objectid import ObjectId
    collection.delete_one({"_id": ObjectId(med_id)})