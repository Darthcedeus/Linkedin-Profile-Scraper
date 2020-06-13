# Linkedin-Profile-Scraper
Python scraper for linkedin profiles. Searches google for profiles based on keywords. This is allows to get profile urls for people who are not part of your linkedin network. Profile information of obtained urls is scrapped and written to CSV. All user information pretaining to Experience, Education, Skills, Certifications is scrapped.

## Disclaimer
Linkedin does not allow data scraping and doing so is against their User Agreement.

## Requirements
- Selenium
- BeautifulSoup
- Pandas

## Usage
```
#init driver
driver = webdriver.Chrome('D:\chromedriver.exe')
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

```

## Currently Working
This scrapper was last tested on June 14, 2020.
