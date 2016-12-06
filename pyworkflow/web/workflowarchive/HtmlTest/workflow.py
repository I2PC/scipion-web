# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import string, random

class Workflow(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.base_url = "http://0.0.0.0:8000"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.workflowName= "wf_" + ''.join(random.choice(string.lowercase) for x in range(16))
    
    def test_workflow(self):
        #connect and paint upload workflow form
        driver = self.driver
        driver.get(self.base_url + "/workflowarchive/")

        #fill in form using a random workflow name
        driver.find_element_by_id("id_workflowName").clear()
        driver.find_element_by_id("id_workflowName").send_keys(self.workflowName)
        driver.find_element_by_id("id_description").clear()
        driver.find_element_by_id("id_description").send_keys("Here goes a description of the tests")
        driver.find_element_by_id("id_file").clear()
        driver.find_element_by_id("id_file").send_keys("/home/roberto/Scipion/scipion-web/pyworkflow/web/workflowarchive/HtmlTest/workflow.json")
        
        #wait two second before sending workflow
        time.sleep(2)
        driver.find_element_by_css_selector("button[type=\"submit\"]").click()
        
        # chek that resul contain magic string
        import re    
        returnedText = driver.find_element_by_css_selector("div.workFlowForm").text
        text_found = re.search('workflow uploaded', returnedText)
        self.assertNotEqual(text_found, None)
        text_found = re.search('hi you', returnedText)
        self.assertEqual(text_found, None)

        # wait a bit before clossing window
        time.sleep(3)
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
