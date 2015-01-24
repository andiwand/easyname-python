import urllib.parse as urlparse

from selenium.webdriver.support.select import Select

class EasynameBot:
    def __init__(self, webdriver):
        self.__driver = webdriver
    def auth(self, username, password):
        self.__driver.get("https://my.ezname.com/en/login")
        
        e = self.__driver.find_element_by_id("username")
        e.send_keys(username)
        
        e = self.__driver.find_element_by_id("password")
        e.send_keys(password)
        
        e = self.__driver.find_element_by_id("submit")
        e.click()
    def is_auth(self):
        self.__driver.get("https://my.ezname.com")
        return "login" not in self.__driver.current_url
    def domains(self):
        self.__driver.get("https://my.ezname.com/domains/")
        table = self.__driver.find_element_by_id("cp_domain_table")
        
        rows = table.find_elements_by_tag_name("tr")
        result = []
        first_row = True
        for row in rows:
            if first_row:
                first_row = False
                continue
            span = row.find_element_by_class_name("domainname")
            name = span.text
            
            domainid = None
            links = row.find_elements_by_tag_name("a")
            for link in links:
                href = link.get_attribute("href")
                params = urlparse.parse_qs(urlparse.urlparse(href).query)
                if "domain" in params:
                    domainid = params["domain"][0]
                    break
            result.append((domainid, name))
        
        return result
    def dns_entries(self, domainid):
        self.__driver.get("https://my.ezname.com/domains/settings/dns.php?domain=%s" % domainid)
        e = self.__driver.find_element_by_id("cp_domains_dnseintraege")
        rows = e.find_elements_by_tag_name("tr")
        result = []
        first_row = True
        for row in rows:
            if first_row:
                first_row = False
                continue
            cells = row.find_elements_by_tag_name("td")
            data = [c.text for c in cells]
            
            dnsid = None
            links = row.find_elements_by_tag_name("a")
            for link in links:
                href = link.get_attribute("href")
                params = urlparse.parse_qs(urlparse.urlparse(href).query)
                if "id" in params:
                    dnsid = params["id"][0]
                    break
            
            result.append((dnsid, data[0], data[1], data[2], data[3], data[4]))
        return result
    def __clear_send_keys(self, element, string):
        if not string: return
        element.clear()
        element.send_keys(string)
    def __select(self, element, string):
        if string: Select(element).select_by_value(string)
    def __dns_fill(self, record, record_type, content, ttl, priority):
        name = self.__driver.find_element_by_name("name")
        suffix = name.find_element_by_xpath("..").text
        if record and not record.endswith(suffix): raise ValueError("invalid domain")
        self.__clear_send_keys(name, record)
        self.__select(self.__driver.find_element_by_name("type"), record_type)
        self.__clear_send_keys(self.__driver.find_element_by_name("content"), content)
        self.__clear_send_keys(self.__driver.find_element_by_name("prio"), priority)
        self.__clear_send_keys(self.__driver.find_element_by_name("ttl"), ttl)
        self.__driver.find_element_by_name("commit").click()
    def dns_add(self, domainid, record, record_type, content, ttl, priority):
        self.__driver.get("https://my.ezname.com/domains/settings/form.php?domain=%s" % domainid)
        self.__dns_fill(record, record_type, content, ttl, priority)
    def dns_remove(self, domainid, recordid):
        self.__driver.get("https://my.ezname.com/domains/settings/delete_record.php?domain=%s&id=%s&confirm=1" % (domainid, recordid))
    def dns_edit(self, domainid, recordid, record, record_type, content, ttl, priority):
        self.__driver.get("https://my.ezname.com/domains/settings/form.php?domain=%s&id=%s" % (domainid, recordid))
        self.__dns_fill(record, record_type, content, ttl, priority)
    def close(self):
        self.__driver.close()
