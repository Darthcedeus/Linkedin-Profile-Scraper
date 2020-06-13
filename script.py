from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import time
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import traceback

#init driver
driver = webdriver.Chrome('D:\chromedriver.exe')

class School:
    def __init__(self):
        self.name = ''
        self.years = ''
        self.program = ''

    def __str__(self):
        return "name: {}, program: {}, years: {} ".format(self.name, self.years, self.program)

class Experience:
    def __init__(self):
        self.company = ''
        self.years = ''
        self.position = []

    def __str__(self):
        return "company: {}, yeasrs: {}, positions: {}".format(self.company, self.years, self.position)

class Profile:
    def __init__(self):
        self.name = ''
        self.job_title = ''
        self.schools = []
        self.experiences = []
        self.skills = []
        self.certifications = []
        self.url = ''

def setup_auth(username, password):
    try:
        driver.get('https://www.linkedin.com/')
        # move to signin page
        driver.find_element_by_xpath('//a[text()="Sign in"]').click()

        #wait for page to load
        #WebDriverWait(driver,  10).until(EC.presence_of_element_located((By.ID, 'username')))
        time.sleep(1)
        username_input = driver.find_element_by_name('session_key')
        username_input.send_keys(username)
        password_input = driver.find_element_by_name('session_password')
        password_input.send_keys(password)

        # click on the sign in button
        driver.find_element_by_xpath('//button[text()="Sign in"]').click()
        if driver.current_url == 'https://www.linkedin.com/checkpoint/lg/login-submit':
            driver.quit()
            sys.exit('Authentication failed')
        else:
            print("Authenticated")
        return driver
    except BaseException as error:
        sys.exit('An exception occurred: {}'.format(error))

def scrap_school_data(soup):
    #get list of schools
    schools = soup.select(".pv-entity__degree-info") #contains school names and programs
    school_years = soup.select(".pv-entity__dates")  #contains years attended

    schools_ = []
    index_count = 0

    for item in schools:
        s = School()
        #extract school name
        s.name = item.select('.pv-entity__school-name')[0].get_text().strip()
        #extract degree (program) name
        degree_name = item.select('.pv-entity__comma-item')
        degree_name_ = ''
        for item_ in degree_name:
            degree_name_ = degree_name_ + ',' + item_.get_text().strip()
        s.program = degree_name_
        #extract years
        try:
            s.years = school_years[index_count].select('time')[0].get_text() + ' - ' + school_years[index_count].select('time')[1].get_text()
            index_count = index_count + 1
        except:
            pass #pass if years extraction fails, or years not found
        schools_.append(s)

    return schools_

def scrap_experience_data():
    #click on show more Experience
    try:
        #if chat box is open, close it
        chat_box = driver.find_element_by_class_name('msg-overlay-bubble-header')
        if "minimize" in chat_box.text:
            chat_box.click()
        #scroll to button, and expand more items
        flag_show_more = True
        while(flag_show_more):
            try:
                ActionChains(driver).move_to_element(driver.find_element_by_class_name('link-without-hover-state')).perform()
                time.sleep(2)
                driver.find_element_by_class_name('link-without-hover-state').click()
            except:
                #all menues expanded
                flag_show_more = False

    except BaseException as error:
        #no more experience
        print("Error occurred when expanding menues")
        print('An exception occurred: {}'.format(error))


    try:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        s = soup.select('#experience-section .ember-view , .mb2')
        exp = []
        for item in s:
            if len(item.select('.pv-entity__summary-info')) != 0 :
                #experience with one postion at company
                exp_ = Experience()
                exp_.position.append(item.select('.t-16.t-black.t-bold')[0].get_text())
                exp_.company = item.select('.pv-entity__secondary-title.t-14.t-black.t-normal')[0].get_text().strip()
                exp_.years = item.select('.pv-entity__date-range.t-14.t-black--light.t-normal')[0].select('span')[1].get_text()
                exp.append(exp_)
            elif len(item.select('.pv-entity__company-summary-info')) !=0 :
                #Experience with multiple postion at company
                exp_ = Experience()
                exp_.company = item.select('.pv-entity__company-summary-info')[0].select('.t-16.t-black.t-bold')[0].select('span')[1].get_text()
                positions = item.select('.pv-entity__summary-info-v2')
                pos_years = ''
                pos_count = 1
                for position in positions:
                    exp_.position.append(position.select('.t-14.t-black.t-bold')[0].select('span')[1].get_text())
                    pos_years = pos_years + 'postion#' + str(pos_count) + ': ' + position.select('.pv-entity__date-range')[0].select('span')[1].get_text() + ', '
                    pos_count = pos_count + 1
                if len(exp_.position) != 0:
                    exp_.years = pos_years
                    exp.append(exp_)
        #remove duplicate entries
        exp_refined = []
        exp_refined.append(exp[0])
        for item in exp:
            if item.company != exp_refined[-1].company:
                exp_refined.append(item)
        return exp_refined
    except BaseException as error:
        #no more experience
        print("Error occurred when extracting experience data")
        print('An exception occurred: {}'.format(error))


def scrap_skills_data():
    #skills
    try:
        #scroll to show moe button
        try:
            html = driver.find_element_by_tag_name('html')
            html.send_keys(Keys.PAGE_UP)
            time.sleep(1)
            ActionChains(driver).move_to_element(driver.find_element_by_class_name('pv-skill-categories-section')).perform()
            time.sleep(2)
            driver.find_element_by_class_name('pv-skills-section__additional-skills').click()
        except BaseException as error:
            print("Error occurred when clicking on more skills")
            print('An exception occurred: {}'.format(error))


        #extract skills
        skills = []
        soup = BeautifulSoup(driver.page_source, 'lxml')
        s = soup.select('.pv-skill-categories-section')
        skills_ = s[0].select('.t-black.t-bold')
        for item in skills_:
            skills.append(item.get_text().strip())
        return skills
    except BaseException as error:
        if len(s) == 0:
            print("No skills found")
        else:
            print("Error extracting skills")
            print('An exception occurred: {}'.format(error))


def scrap_certifications_data():
    #extract licnese and certifications
    s = ''
    try:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        s = soup.select('.pv-profile-section--certifications-section')
        certs = s[0].select('.pv-certifications__summary-info')
        certifications = []
        for item in certs:
            certifications.append(item.select('.t-16.t-bold')[0].get_text())
        return certifications
    except BaseException as error:
        if len(s) == 0:
            print("No certifications found")
        else:
            print("Error extracting certification")
            print('An exception occurred: {}'.format(error))


def find_profile_google(company_name, position):
    driver.get('https://www.google.com/')
    search_input = driver.find_element_by_name('q')

    # let google find any linkedin user with keyword "founder" and "smartpath"
    search_input.send_keys('site:linkedin.com/in/ AND "{}" AND "{}"'.format(company_name, position))
    search_input.send_keys(Keys.RETURN)

    # grab all linkedin profiles from first page at Google
    profiles = driver.find_elements_by_xpath('//*[@class="r"]/a[1]')
    profiles = [profile.get_attribute('href') for profile in profiles]

    print("Profiles found:")
    print(profiles)
    return profiles

def scrap_profile(profile_url):
    print('Now scrapping: ' + profile_url)
    try:
        driver.get(profile_url)
        flag = True
        retry_count = 0
        while(retry_count < 5 and flag):
            #go to bottom of page
            html = driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)
            time.sleep(4)
            #break
            retry_count = retry_count + 1
            try:
                #check if interests sections is loaded
                driver.find_elements_by_class_name("pv-interests-section")
                flag = False
            except:
                print('interests section not loaded, trying again')
                continue

        profile_data = Profile()
        soup = BeautifulSoup(driver.page_source, 'lxml')

        #extract name
        profile_data.name = soup.select('.t-24')[0].get_text().strip()
        #extract title
        profile_data.job_title = soup.select('.t-18')[0].get_text().strip()
        #extract school data
        profile_data.schools = scrap_school_data(soup)
        #extract experience data
        profile_data.experiences = scrap_experience_data()
        #extract skill data
        profile_data.skills = scrap_skills_data()
        #extract certifications data
        profile_data.certifications = scrap_certifications_data()
        #set profile url
        profile_data.url = profile_url

        return profile_data
    except BaseException as error:
        print('failed to scrap profile data')
        print('An exception occurred: {}'.format(error))
        traceback.print_exc()

def profile_to_frame(profile):
    try:
        frame = pd.DataFrame()
        frame['name'] = [profile.name]
        frame['job_title'] = [profile.job_title]
        frame['url'] = [profile.url]

        count = 1
        for school in profile.schools:
            frame['school_' + str(count) + '_name'] = [school.name]
            frame['school_' + str(count) + '_years'] = [school.years]
            frame['school_ ' + str(count) + '_program'] = [school.program]
            count = count + 1

        count = 1
        for exp in profile.experiences:
            frame['experience_' + str(count) + '_company'] = [exp.company]
            frame['experience_' + str(count) + '_years'] = [exp.years]
            pos_count = 1
            for pos in exp.position:
                frame['experience_' + str(count) + '_position_' + str(pos_count)] = [pos]
                pos_count = pos_count + 1
            count = count + 1

        if profile.skills is not None:
            frame['skills'] = [', '.join(profile.skills)]

        if profile.certifications is not None:
            frame['certifications'] = [', '.join(profile.certifications)]

        return frame
    except BaseException as error:
        print('failed creating profile frame')
        print('An exception occurred: {}'.format(error))
        traceback.print_exc()

#############################################################3
def test():
    #signin to linkedin
    driver = setup_auth(username='', password='')
    #getting profile links from google
    profile_links_google = find_profile_google(company_name='smartpath', position='founder')
    #scrap profile data
    frame = pd.DataFrame()
    for url in profile_links_google:
        #scrap profile
        profile = scrap_profile(profile_url=url)
        #convert extracted informtion to data frame
        profile_frame = profile_to_frame(profile)
        #append data frame to main frame
        frame = frame.append(profile_frame)
    #write to file
    frame.to_csv('results_.csv')
    driver.quit()

test()
