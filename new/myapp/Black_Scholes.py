import datetime as dt
import requests
import numpy as np
import os  
import base64
from bson import ObjectId
from pymongo import MongoClient
from scipy.stats import norm

class FinancialDataProcessor:
    
    def __init__(self, cleaned_data):
        # Initialize with cleaned form data
        self.dic = cleaned_data

    def mongoconnection(self):
        pem_base64 = os.getenv("MongoConnection")

        if pem_base64:
            pem_path = "/tmp/X509-cert.pem"
            with open(pem_path, "wb") as pem_file:
                pem_file.write(base64.b64decode(pem_base64))
            return pem_path
        else:
            raise ValueError("MongoConnection environment variable is missing!")

    def options_data(self):
        key = "YPBRFBE73PWU9YKC"
        date = "2024-09-10"
        url = f"https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol=IBM&date={date}&apikey={key}"
        
        headers = {"Authentication": key}
        response = requests.get(url, headers=headers)
        data = response.json()

        try:
            pem_path = self.mongoconnection()
            # conn = MongoClient("mongodb+srv://cluster0.qkxvm.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsCAFile=C%3A%5CUsers%5CRehan+Khan%5CDownloads%5CX509-cert-4423045577537522277.pem&tlsCertificateKeyFile=C%3A%5CUsers%5CRehan+Khan%5CDownloads%5CX509-cert-4423045577537522277.pem&tlsAllowInvalidHostnames=true&tlsAllowInvalidCertificates=true")
            conn = MongoClient("mongodb+srv://cluster0.qkxvm.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509", tls=True, tlsCertificateKeyFile=pem_path)
            print("Connection Successful")
        except:
            print("Connection Failed")

        db = conn.get_database("F1_races")
        collection = db.get_collection("Options")
        #collection.insert_many(data["data"])

        expiration = self.dic["expiration"]
        strike = float(self.dic["strike"])
        strike = f"{strike:.2f}"
        opt_type = self.dic["type"]

        results = collection.find({"expiration": expiration, "strike": strike, "type": opt_type})
        return list(results)

    def get_curr_stk(self):
        key = "66eaf63bb1c5f7.10647466"
        url = f"https://eodhd.com/api/eod/IBM?period=2024-09-12to2024-09-13&api_token={key}&fmt=json"
        data = requests.get(url)

        try:
            pem_path = self.mongoconnection()
            # conn = MongoClient("mongodb+srv://cluster0.qkxvm.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsCAFile=C%3A%5CUsers%5CRehan+Khan%5CDownloads%5CX509-cert-4423045577537522277.pem&tlsCertificateKeyFile=C%3A%5CUsers%5CRehan+Khan%5CDownloads%5CX509-cert-4423045577537522277.pem&tlsAllowInvalidHostnames=true&tlsAllowInvalidCertificates=true")
            conn = MongoClient("mongodb+srv://cluster0.qkxvm.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509", tls=True, tlsCertificateKeyFile=pem_path)
            print("Connection Successful")
        except:
            print("Connection Failed")

        db = conn.get_database("F1_races")
        collection = db.get_collection("Stock_Price")
        #collection.insert_many(data.json())

        date = self.dic["date"]
        results = collection.find({"date": date})

        return list(results)

    def treasury_bond_data(self):
        key = "daf3283a35a27a83ec90bedb4f951350"
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={key}&file_type=json&observation_start=2024-08-15&observation_end=2024-09-15"
        headers = {"Authentication": key}
        data = requests.get(url, headers=headers)

        try:
            pem_path = self.mongoconnection()
            # conn = MongoClient("mongodb+srv://cluster0.qkxvm.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority&appName=Cluster0&tls=true&tlsCAFile=C%3A%5CUsers%5CRehan+Khan%5CDownloads%5CX509-cert-4423045577537522277.pem&tlsCertificateKeyFile=C%3A%5CUsers%5CRehan+Khan%5CDownloads%5CX509-cert-4423045577537522277.pem&tlsAllowInvalidHostnames=true&tlsAllowInvalidCertificates=true")
            conn = MongoClient("mongodb+srv://cluster0.qkxvm.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509", tls=True, tlsCertificateKeyFile=pem_path)
            print("Connection Successful")
        except:
            print("Connection Failed")

        db = conn.get_database("F1_races")
        collection = db.get_collection("RateOIntrst")
        #collection.insert_one(data.json())

        result = collection.find({"_id": ObjectId("66e9a96d2dbcf210e26503ba")}, {"observations.value": 1, "_id": 0, "observations.date": 1, "_id": 0})
        documents = list(result)
        return documents[0]['observations']

    def bs_call(self, opt_dta, rsfi, stk_pr):
        date = self.dic["date"]
        S = stk_pr[0]["close"]
        K = float(opt_dta[0]["strike"])
        sig = float(opt_dta[0]["implied_volatility"])
        r = float([i for i in rsfi if i["date"] == date][0]["value"]) / 100 
        T = dt.datetime.strptime(opt_dta[0]["expiration"], '%Y-%m-%d') - dt.datetime.strptime(opt_dta[0]["date"], "%Y-%m-%d")
        T = T.days / 365
        N = norm.cdf
        d1 = (np.log(S/K) + (r + sig ** 2 / 2) * T) / (sig * np.sqrt(T))
        d2 = d1 - sig * np.sqrt(T)

        return S * N(d1) - N(d2) * K * np.exp(-r * T)

    def bs_put(self, opt_dta, rsfi, stk_pr):
        date = self.dic["date"]
        S = stk_pr[0]["close"]
        K = float(opt_dta[0]["strike"])
        sig = float(opt_dta[0]["implied_volatility"])
        r = float([i for i in rsfi if i["date"] == date][0]["value"]) / 100 
        T = dt.datetime.strptime(opt_dta[0]["expiration"], '%Y-%m-%d') - dt.datetime.strptime(opt_dta[0]["date"], "%Y-%m-%d")
        T = T.days / 365 # in terms of years
        N = norm.cdf
        d1 = (np.log(S/K) + (r + sig ** 2 / 2) * T) / (sig * np.sqrt(T))
        d2 = d1 - sig * np.sqrt(T)

        return S * -N(-d1) + N(-d2) * K * np.exp(-r * T)

    def result(self):
        opt_dta = self.options_data()
        rsfi = self.treasury_bond_data()
        stk_pr = self.get_curr_stk()
    
        if self.dic["type"] == "put":
            return self.bs_put(opt_dta=opt_dta, rsfi=rsfi, stk_pr=stk_pr)
        else:
            return self.bs_call(opt_dta=opt_dta, rsfi=rsfi, stk_pr=stk_pr)
