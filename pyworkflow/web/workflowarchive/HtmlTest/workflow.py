# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import string, random
import tempfile

example_content="""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head profile="http://selenium-ide.openqa.org/profiles/test-case">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="selenium.base" href="http://0.0.0.0:8000/" />
<title>workflow</title>
</head>
<body>
<table cellpadding="1" cellspacing="1" border="1">
<thead>
<tr><td rowspan="1" colspan="3">workflow</td></tr>
</thead><tbody>
<tr>
	<td>open</td>
	<td>/workflowarchive/</td>
	<td></td>
</tr>
<tr>
	<td>type</td>
	<td>id=id_workflowName</td>
	<td>workflow_random</td>
</tr>
<tr>
	<td>type</td>
	<td>id=id_description</td>
	<td>Here goes a description of the tests</td>
</tr>
<tr>
	<td>type</td>
	<td>id=id_file</td>
	<td>/home/roberto/Scipion/scipion-web/pyworkflow/web/workflowarchive/HtmlTest/workflow.json</td>
</tr>
<tr>
	<td>clickAndWait</td>
	<td>css=button[type=&quot;submit&quot;]</td>
	<td></td>
</tr>
<tr>
	<td>assertText</td>
	<td>css=div.workFlowForm</td>
	<td>workflow uploaded </td>
</tr>

</tbody></table>
</body>
</html>"""

class Workflow(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.base_url = "http://0.0.0.0:8000"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.workflowName= "wf_" + ''.join(random.choice(string.lowercase) for x in range(16))
        self.createJsonFile()

    def createJsonFile(self):
	self.f = tempfile.NamedTemporaryFile(delete=False)
        self.f.write(example_content)
        self.f.close()

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
        driver.find_element_by_id("id_file").send_keys(self.f.name)
        
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
        os.unlink(self.f.name)
        
    
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
