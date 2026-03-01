from datetime import datetime

class Medication:
    def __init__(self, name, dosage, time, frequency, start_date, end_date):
        self.name = name
        self.dosage = dosage
        self.time = time
        self.frequency = frequency
        self.start_date = str(start_date)
        self.end_date = str(end_date)
        self.created_at = datetime.now()

    def to_dict(self):
        return self.__dict__