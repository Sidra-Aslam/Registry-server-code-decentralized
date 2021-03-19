import csv
# class to save time in timeObj, this will be accessed in all files
class CSVLogger(object):
    # list object to hold n times
    timeList = []
    # dict object to hold time parameters
    timeObj = {}
    
    # method to save time object to list (this will be called n times)
    @classmethod
    def log_run(cls):
        cls.timeList.append(cls.timeObj)
        cls.timeObj = {}
    
    # method to create csv for create_data (Asymmetric)
    @classmethod
    def asym_create_data_csv(cls):
        with open('asymmetric_create_data.csv', 'w', newline='') as csvfile:
            # create csv writer object
            writer = csv.writer(csvfile)
            # header row of csv
            writer.writerow(['Time to verify permission', 'Data encryption (asymmetric key) time', 'DHT storage time', 'Blockchain storage time', 'Overall time'])
            # iterate loop n times    
            for time in cls.timeList:
                # write times from list object to csv file
                writer.writerow([time['RbacTime'], time['AsymmetricEncryption'], time['DhtStorage'], time['BlockchainStorageTime'], time['OverallTime']])
        
        # clear variables after csv is saved
        cls.timeList=[]
        cls.timeObj={}

    # method to create csv for create_data (Symmetric)
    @classmethod
    def sym_create_data_csv(cls):

        with open('symmetric_create_data.csv', 'w', newline='') as csvfile:
            # create csv writer object
            writer = csv.writer(csvfile)
            # header row of csv
            writer.writerow(['Time to verify permission','Data encryption (symmetric key) time', 'DHT storage time', 'Blockchain storage time', 'Overall time'])
            # iterate loop n times    
            for time in cls.timeList:
                # write times from list object to csv file
                writer.writerow([time['RbacTime'], time['SymmetricEncryption'], time['DhtStorage'], time['BlockchainStorageTime'], time['OverallTime']])
        # clear variables after csv is saved        
        cls.timeList=[]
        cls.timeObj={}
    
    # method to create csv for update_data (Asymmetric)
    @classmethod
    def asym_update_data_csv(cls):
        with open('asymmetric_update_data.csv', 'w', newline='') as csvfile:
            # create csv writer object
            writer = csv.writer(csvfile)
            # header row of csv
            writer.writerow(['Time to verify permission', 'Blockchain read time', 'Asymmetric encryption time', 'DHT storage time', 'Overall time'])
            # iterate loop n times    
            for time in cls.timeList:
                # write times from list object to csv file
                writer.writerow([time['RbacTime'], time['BlockchainReadTime'], time['AsymmetricEncryption'], time['DhtStorage'],  time['OverallTime']])
        
        # clear variables after csv is saved
        cls.timeList=[]
        cls.timeObj={}

    # method to create csv for update_data (Symmetric)
    @classmethod
    def sym_update_data_csv(cls):
        with open('asymmetric_update_data.csv', 'w', newline='') as csvfile:
            # create csv writer object
            writer = csv.writer(csvfile)
            # header row of csv
            writer.writerow(['Time to verify permission', 'Blockchain read time', 'Symmetric encryption time', 'DHT storage time', 'Overall time'])
            # iterate loop n times    
            for time in cls.timeList:
                # write times from list object to csv file
                writer.writerow([time['RbacTime'], time['BlockchainReadTime'], time['SymmetricEncryption'], time['DhtStorage'],  time['OverallTime']])
        
        # clear variables after csv is saved
        cls.timeList=[]
        cls.timeObj={}

    # method to create csv for read data
    @classmethod
    def read_data_csv(cls):
        with open('read_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # header row of csv
            writer.writerow(['Time to verify permission','Blockchain read time', 'Data reading request time', 'Ring verification time', 'Decryption with public key', 'Overall time'])
            # iterate loop n times    
            for time in cls.timeList:
                # write times from list object to csv file
                writer.writerow([time['RbacTime'], time['BlockchainReadTime'], time['DataReadRequestTime'], time['VerifyRing'], time['AsymmetricDecryption'], time['OverallTime']])
        # clear variables after csv is saved 
        cls.timeList=[]
        cls.timeObj={}

    # method to create csv for delete data
    @classmethod
    def delete_data_csv(cls):
        with open('delete_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time to verify permission', 'Blockchain read time', 'DHT update time', 'Overall time'])
            # iterate loop n times    
            for time in cls.timeList:
                # write times from list object to csv file
                writer.writerow([time['RbacTime'], time['BlockchainReadTime'], time['DhtStorage'], time['OverallTime']])
        # clear variables after csv is saved
        cls.timeList=[]
        cls.timeObj={}