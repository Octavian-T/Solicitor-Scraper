import re
from bs4 import BeautifulSoup
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import pandas as pd
from urllib.parse import urlparse


class ContactParser:

    def __init__(self):
        self.email_stop_vals = pd.read_csv(f"input/stop_email.csv")["email"]
        self.phone_stop_vals = pd.read_csv(f"input/stop_phone.csv")["phone"]

    def parse_phone(self, html, mobile=False):
        phones = []
        soup = BeautifulSoup(html, "html.parser")
        string = ""
        for ele in soup.find_all():
            for attr in ele.attrs.values():
                if type(attr) == list:
                    string = f"{string} {' '.join(attr)}"
                else:
                    string = f"{string} {attr}"
        matcher = phonenumbers.PhoneNumberMatcher(f"{soup.get_text(' ')} {string}", "GB")
        if matcher.has_next():
            for match in matcher:
                # country check
                if match.number.country_code != 44:
                    continue
                found = False
                # stop check
                for stop in self.phone_stop_vals:
                    if phonenumbers.format_number(phonenumbers.parse(str(stop), "GB"), phonenumbers.PhoneNumberFormat.INTERNATIONAL) == phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL):
                        found = True
                        break
                if not found:
                    # mobile check
                    if not mobile:
                        if not carrier._is_mobile(number_type(phonenumbers.parse(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL), "GB"))):
                            phones.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
                    else:
                        if carrier._is_mobile(number_type(phonenumbers.parse(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL), "GB"))):
                            phones.append(phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))
                else:
                    continue
            if phones:
                if mobile:
                    if len(phones) == 1:
                        return ", ".join(list(set(phones)))
                    else:
                        return None
                else:
                    if len(phones) > 0 and len(phones) < 3:
                        return ", ".join(list(set(phones)))
                    else:
                        return None
            else:
                return None
        else:
            return None

    @staticmethod
    def regex_parse(regex, html, element_par=False):
        values = []
        soup = BeautifulSoup(html, "html.parser")
        if element_par:
            for ele in soup.find_all():
                for attr in ele.attrs.values():
                    if type(attr) == list:
                        match = re.findall(regex, ' '.join(attr))
                        if type(match) == list:
                            for value in match:
                                values.append(value)
                        elif type(match) is not None:
                            values.append(match)
                    else:
                        match = re.findall(regex, attr)
                        if match:
                            if type(match) == list:
                                for value in match:
                                    values.append(value)
                            elif type(match) is not None:
                                values.append(match)
        else:
            match = re.findall(regex, soup.get_text(' '))
            if match:
                if type(match) == list:
                    for value in match:
                        values.append(value)
                elif type(match) is not None:
                    values.append(match)
        if values:
            return values
        else:
            return None

    def parse_email(self, name, html):
        EMAIL_REGEX = r'[\w.+-]+@[\w-]+\.[\w.-]+'
        emails = self.regex_parse(html=html, regex=EMAIL_REGEX)
        # stop check
        if emails:
            _emails = []
            for value in emails:
                found = False
                for stop in self.email_stop_vals:
                    if stop.lower() in value.lower():
                        found = True
                        break
                if not found:
                    _emails.append(value)
                else:
                    continue
            # name check
            if _emails:
                __emails = []
                if len(_emails) > 1:
                    for _email in _emails:
                        for sub in name.split(" "):
                            if sub.lower() in _email.lower():
                                __emails.append(_email)
                    if __emails:
                        return ", ".join(list(set(__emails)))
                else:
                    return ", ".join(_emails)
            else:
                return None
        else:
            return None

    def parse_linkedin(self, html):
        LINKEDIN_REGEX = r'linkedin\.com\/in\/[A-z0-9_-]+\/?|'\
                         r'uk\.linkedin\.com\/in\/[A-z0-9_-]+\/?'
        linkedins = self.regex_parse(html=html, regex=LINKEDIN_REGEX, element_par=True)
        if linkedins:
            new_linkedins = []
            for linkedin in linkedins:
                url = urlparse(linkedin)
                if url.scheme == "":
                    url = url._replace(scheme="https")
                new_linkedins.append(url.geturl().replace("///", "//"))
            return ", ".join(list(set(new_linkedins)))
        else:
            return None
