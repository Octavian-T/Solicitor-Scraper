# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd
import requests
import json


class LtProfileScraperPipeline:
    def __init__(self):
        #
        # Stats
        #
        self.firms_stats = {}
        self.general_stats = {
            "links": 0,
            "matches": 0,
            "emails": 0,
            "linkedins": 0,
            "mobiles": 0,
            "phones": 0,
            "bios": 0,
            "titles": 0,
            "sectors": 0
        }
        #
        # Data
        #
        self.profiles = []
        self.failed = []
        self.error = []

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {open("input/token.txt").read()}',
            'Accept': 'application/json'
        }
        self.url = "https://legaltarget.backend-api.io/api/solicitors/"

    def process_item(self, item, spider):
        #
        # Create Item Object
        #
        if item["Name"] is not None:
            profiles_dict = {
                "organisation": item["Firm"],
                "name": item["Name"],
                "profile_url": item["Url"],
            }
            if item["Title"] is not None and item["Title"] != "":
                self.general_stats["titles"] = self.general_stats["titles"] + 1
            if item["Bio"] is not None and item["Bio"] != "":
                self.general_stats["bios"] = self.general_stats["bios"] + 1
            if item["Sector"] is not None and item["Sector"] != "":
                for sector in item["Sector"].split(", "):
                    if sector != "" and sector is not None:
                        self.general_stats["sectors"] = self.general_stats["sectors"] + 1
            if item["Phone"] is not None:
                counter = 0
                for phone in item["Phone"].split(", "):
                    if phone != "" and phone is not None:
                        self.general_stats["phones"] = self.general_stats["phones"] + 1
                        if counter == 0:
                            profiles_dict["telephone"] = phone
                        counter = counter + 1
            if item["Mobile"] is not None:
                counter = 0
                for mobile in item["Mobile"].split(", "):
                    if mobile != "" and mobile is not None:
                        self.general_stats["mobiles"] = self.general_stats["mobiles"] + 1
                        if counter == 0:
                            profiles_dict["mobile"] = mobile
                        counter = counter + 1
            if item["Email"] is not None:
                counter = 0
                for email in item["Email"].split(", "):
                    if email != "" and email is not None:
                        self.general_stats["emails"] = self.general_stats["emails"] + 1
                        if counter == 0:
                            profiles_dict["email"] = email
                        counter = counter + 1
            if item["Linkedin"] is not None:
                counter = 0
                for linkedin in item["Linkedin"].split(", "):
                    if linkedin != "" and linkedin is not None:
                        self.general_stats["linkedins"] = self.general_stats["linkedins"] + 1
                        if counter == 0:
                            profiles_dict["linkedin"] = linkedin
                        counter = counter + 1

            response = self.send_lt(profiles_dict)
            if response != False and response["data"][0]["result"]["matched"]:
                self.general_stats["matches"] = self.general_stats["matches"] + 1
                print(f"response: {response}")
            else:
                self.save_failed_profile(profiles_dict)
                print("could not send to LT")

            self.general_stats["links"] = self.general_stats["links"] + 1
            self.save_profile(profiles_dict)
            self.save_firm_stats(item["Firm_URL"])
            self.save_general_stats()

            return item
        else:
            self.save_error(item)
            return None

    def send_lt(self, profile_dict):
        #
        # Send to LT
        #
        payload = json.dumps(profile_dict)
        response = requests.request("PATCH", self.url, headers=self.headers, data=payload)
        try:
            response = json.loads(response.content)
            return response
        except Exception as e:
            print("failed to send to LT")
            return False

    def save_general_stats(self):
        #
        # General Stats Recorder
        #
        df_gs = pd.DataFrame(self.general_stats, index=[0])
        df_gs.to_csv(f"output/general_stats.csv")

    def save_firm_stats(self, Firm_URL):
        #
        # Firm Stats Recorder
        #
        if Firm_URL in self.firms_stats:
            self.firms_stats[Firm_URL] = self.firms_stats[Firm_URL] + 1
        else:
            self.firms_stats[Firm_URL] = 1
        df_fs = pd.DataFrame(self.firms_stats, index=[0])
        df_fs.to_csv(f"output/firms_stats.csv")

    def save_failed_profile(self, profile_dict):
        self.failed.append(pd.DataFrame(profile_dict, index=[0]))
        df_f = pd.concat(self.failed)
        df_f.to_csv(f"output/failed_match.csv", index=[0])

    def save_error(self, profile_dict):
        self.error.append(pd.DataFrame([profile_dict], index=[0]))
        df_e = pd.concat(self.error)
        df_e.to_csv(f"output/error.csv", index=[0])

    def save_profile(self, profile_dict):
        self.profiles.append(pd.DataFrame(profile_dict, index=[0]))
        df = pd.concat(self.profiles)
        df.to_csv(f"output/profile_data.csv", index=[0])
