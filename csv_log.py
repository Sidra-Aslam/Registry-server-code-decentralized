#This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
import csv
import pandas as pd

# class to save time in timeObj, this will be accessed in all files
class CSVLogger(object):
    # list object to hold n times
    timeList = []
    # dict object to hold time parameters
    timeObj = {}

    # method to save time object to list (this will be called n times)
    @classmethod
    def save_time(cls):
        cls.timeList.append(cls.timeObj)
        cls.timeObj = {}

    # method to create csv for create_data (Asymmetric)
    @classmethod
    def asym_create_data_csv(cls):
        try:
            # create dataframe from list and rename column names
            df = pd.DataFrame(cls.timeList).rename({'RbacTime': 'Time to verify permission', 
                            'AsymmetricEncryption': 'Data encryption (asymmetric key) time',
                            'DhtStorage':'DHT storage time',
                            'BlockchainStorageTime':'Blockchain storage time',
                            'OverallTime':'Overall time' 
                            }, axis='columns')

            # copy dataframe with ordered columns 
            df = df[['Time to verify permission', 'Data encryption (asymmetric key) time', 'DHT storage time', 
                            'Blockchain storage time', 'Overall time']].copy()
            
            avgVal = df.mean()
            stdVal = df.std()
            minVal = df.min()
            maxVal = df.max()
            
            # calcuation averate, st.d, min, max
            df.loc['Average'] = avgVal 
            df.loc['St Deviation'] = stdVal 
            df.loc['Min'] = minVal
            df.loc['Max'] = maxVal 

            # apply formatting
            # df = df.applymap("{:.8f}".format)

            # save csv
            # df.to_csv("csv_files/asymmetric_create_data.csv")
            # export data in excel sheet
            with pd.ExcelWriter("csv_files/asymmetric_create_data.xlsx") as writer:
                df.to_excel(writer, float_format="%.8f")
        except:
            pass
        finally:
            # clear variables after csv is saved 
            cls.timeList=[]
            cls.timeObj={}

    # method to create csv for create_data (Symmetric)
    @classmethod
    def sym_create_data_csv(cls):
        try:
            # create dataframe from list and rename column names
            df = pd.DataFrame(cls.timeList).rename({'RbacTime': 'Time to verify permission', 
                            'SymmetricEncryption': 'Data encryption (symmetric key) time',
                            'DhtStorage':'DHT storage time',
                            'BlockchainStorageTime':'Blockchain storage time',
                            'OverallTime':'Overall time' 
                            }, axis='columns')
            # copy dataframe with ordered columns
            df = df[['Time to verify permission', 'Data encryption (symmetric key) time', 'DHT storage time', 
                            'Blockchain storage time', 'Overall time']].copy()
            # calcuation averate, st.d, min, max
            avgVal = df.mean()
            stdVal = df.std()
            minVal = df.min()
            maxVal = df.max()
            
            # calcuation averate, st.d, min, max
            df.loc['Average'] = avgVal 
            df.loc['St Deviation'] = stdVal 
            df.loc['Min'] = minVal
            df.loc['Max'] = maxVal 
            # apply formatting
            # df = df.applymap("{:.8f}".format)
            # save csv
            # df.to_csv("csv_files/symmetric_create_data.csv")
            with pd.ExcelWriter("csv_files/symmetric_create_data.xlsx") as writer:
                df.to_excel(writer, float_format="%.8f")
        except:
            pass
        finally:
            # clear variables after csv is saved 
            cls.timeList=[]
            cls.timeObj={}
    
    # method to create csv for update_data (Asymmetric)
    @classmethod
    def asym_update_data_csv(cls):
        try:
            # create dataframe from list and rename column names
            df = pd.DataFrame(cls.timeList).rename({'RbacTime': 'Time to verify permission', 
                            'BlockchainReadTime':'Blockchain read time',
                            'AsymmetricEncryption':'Asymmetric encryption time',
                            'DhtStorage':'DHT storage time',
                            'OverallTime':'Overall time' 
                            }, axis='columns')
            # copy dataframe with ordered columns
            df = df[['Time to verify permission', 'Blockchain read time', 'Asymmetric encryption time', 
                            'DHT storage time', 'Overall time']].copy()
            # calcuation averate, st.d, min, max
            avgVal = df.mean()
            stdVal = df.std()
            minVal = df.min()
            maxVal = df.max()
            
            # calcuation averate, st.d, min, max
            df.loc['Average'] = avgVal 
            df.loc['St Deviation'] = stdVal 
            df.loc['Min'] = minVal
            df.loc['Max'] = maxVal 
            # apply formatting
            # df = df.applymap("{:.8f}".format)
            # save csv
            # df.to_csv("csv_files/asymmetric_update_data.csv")
            with pd.ExcelWriter("csv_files/asymmetric_update_data.xlsx") as writer:
                df.to_excel(writer, float_format="%.8f")
        except:
            pass
        finally:
            # clear variables after csv is saved 
            cls.timeList=[]
            cls.timeObj={}

    # method to create csv for update_data (Symmetric)
    @classmethod
    def sym_update_data_csv(cls):
        try:
            # create dataframe from list and rename column names
            df = pd.DataFrame(cls.timeList).rename({'RbacTime': 'Time to verify permission', 
                            'BlockchainReadTime':'Blockchain read time',
                            'SymmetricEncryption':'Symmetric encryption time',
                            'DhtStorage':'DHT storage time',
                            'OverallTime':'Overall time' 
                            }, axis='columns')
            # copy dataframe with ordered columns
            df = df[['Time to verify permission', 'Blockchain read time', 'Symmetric encryption time', 
                            'DHT storage time', 'Overall time']].copy()
            # calcuation averate, st.d, min, max
            avgVal = df.mean()
            stdVal = df.std()
            minVal = df.min()
            maxVal = df.max()
            
            # calcuation averate, st.d, min, max
            df.loc['Average'] = avgVal 
            df.loc['St Deviation'] = stdVal 
            df.loc['Min'] = minVal
            df.loc['Max'] = maxVal 
            # apply formatting
            # df = df.applymap("{:.8f}".format)
            # save csv
            # df.to_csv("csv_files/symmetric_update_data.csv")
            with pd.ExcelWriter("csv_files/symmetric_update_data.xlsx") as writer:
                df.to_excel(writer, float_format="%.8f")
        except:
            pass
        finally:
            # clear variables after csv is saved 
            cls.timeList=[]
            cls.timeObj={}

    # method to create csv for read data
    @classmethod
    def asym_read_data_csv(cls):
        try:
            # create dataframe from list and rename column names
            df = pd.DataFrame(cls.timeList).rename({'RbacTime': 'Time to verify permission', 
                            'BlockchainReadTime':'Blockchain read time',
                            'EncDecTime':'Encryption/Decryption time',
                            'DhtRead':'DHT read time',
                            'CreateRing':'Ring creation',
                            'VerifyRing':'Ring verification time',
                            'OverallTime':'Overall time' 
                            }, axis=1)
            # copy dataframe with ordered columns
            df = df[['Time to verify permission','Blockchain read time', 'Encryption/Decryption time', 
            'DHT read time', 'Ring creation', 'Ring verification time',  'Overall time']].copy()
            # calcuation averate, st.d, min, max
            avgVal = df.mean()
            stdVal = df.std()
            minVal = df.min()
            maxVal = df.max()
            
            # calcuation averate, st.d, min, max
            df.loc['Average'] = avgVal 
            df.loc['St Deviation'] = stdVal 
            df.loc['Min'] = minVal
            df.loc['Max'] = maxVal 
            # apply formatting
            # df = df.applymap("{:.8f}".format)
            # save csv
            # df.to_csv("csv_files/asymmetric_read_data.csv")
            with pd.ExcelWriter("csv_files/asymmetric_read_data.xlsx") as writer:
                df.to_excel(writer, float_format="%.8f")
        except:
            pass
        finally:
            # clear variables after csv is saved 
            cls.timeList=[]
            cls.timeObj={}

    # method to create csv for read data
    @classmethod
    def sym_read_data_csv(cls):
        try:
            # create dataframe from list and rename column names
            df = pd.DataFrame(cls.timeList).rename({'RbacTime': 'Time to verify permission', 
                            'BlockchainReadTime':'Blockchain read time',
                            'EncDecTime':'Encryption/Decryption time',
                            'DhtRead':'DHT read time',
                            'CreateRing':'Ring creation',
                            'VerifyRing':'Ring verification time',
                            'OverallTime':'Overall time' 
                            }, axis='columns')
            # copy dataframe with ordered columns
            df = df[['Time to verify permission','Blockchain read time', 'Encryption/Decryption time', 
            'DHT read time', 'Ring creation', 'Ring verification time',  'Overall time']].copy()
            # calcuation averate, st.d, min, max
            avgVal = df.mean()
            stdVal = df.std()
            minVal = df.min()
            maxVal = df.max()
            
            # calcuation averate, st.d, min, max
            df.loc['Average'] = avgVal 
            df.loc['St Deviation'] = stdVal 
            df.loc['Min'] = minVal
            df.loc['Max'] = maxVal 
            # apply formatting
            # df = df.applymap("{:.8f}".format)
            # save csv
            # df.to_csv("csv_files/symmetric_read_data.csv")
            with pd.ExcelWriter("csv_files/symmetric_read_data.xlsx") as writer:
                df.to_excel(writer, float_format="%.8f")
        except:
            pass
        finally:
            # clear variables after csv is saved 
            cls.timeList=[]
            cls.timeObj={}
    # method to create csv for delete data
    @classmethod
    def delete_data_csv(cls):
        try:
            # create dataframe from list and rename column names
            df = pd.DataFrame(cls.timeList).rename({'RbacTime': 'Time to verify permission', 
                            'BlockchainReadTime':'Blockchain read time',
                            'DhtStorage':'DHT update time',
                            'OverallTime':'Overall time' 
                            }, axis='columns')
            # copy dataframe with ordered columns
            df = df[['Time to verify permission', 'Blockchain read time', 'DHT update time', 'Overall time']].copy()
            # calcuation averate, st.d, min, max
            avgVal = df.mean()
            stdVal = df.std()
            minVal = df.min()
            maxVal = df.max()
            
            # calcuation averate, st.d, min, max
            df.loc['Average'] = avgVal 
            df.loc['St Deviation'] = stdVal 
            df.loc['Min'] = minVal
            df.loc['Max'] = maxVal 
            # apply formatting
            # df = df.applymap("{:.8f}".format)
            # save csv
            # df.to_csv("csv_files/delete_data.csv")
            with pd.ExcelWriter("csv_files/delete_data.xlsx") as writer:
                df.to_excel(writer, float_format="%.8f")
        except:
            pass
        finally:
            # clear variables after csv is saved 
            cls.timeList=[]
            cls.timeObj={}