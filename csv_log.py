import csv
# class to save time in timeObj, this will be accessed in all files
class CSVLogger(object):
    timeObj = {}
    @staticmethod
    def log(row):
        with open('log.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(row)