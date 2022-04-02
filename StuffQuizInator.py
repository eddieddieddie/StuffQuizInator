from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
# To handle waiting actions to complete...
from selenium.webdriver.support.ui import WebDriverWait

from random import choice
import time
import re
import datetime 

monthsInTheYear = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

driver = webdriver.Firefox(executable_path=r'C:\WebDriver\bin\geckodriver.exe')
#driver.implicitly_wait(5)

## Section one - load the quizes page and find todays morning quiz:
driver.get("https://www.stuff.co.nz/national/quizzes")
content = driver.find_elements(by=By.CSS_SELECTOR, value=".list-asset-strap-container .it-article-headline")
# Stuff has a week or so of older and other quizzes on this page. We only want todays morning quiz. Check each descritpion to find todays.
current_time = datetime.datetime.now()
currentMonth = monthsInTheYear[current_time.month-1]
dateSearchRegex = f'Morning[ \w:]+{currentMonth} {current_time.day}'
print("Searching for: " + dateSearchRegex)
for e in content:
    if re.search(dateSearchRegex, e.text, re.I):
        print("Found todays quiz: " +e.text)
        #todaysMorningQuizUrl = e.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
        linkToTodaysMorningQuiz = e.find_element(by=By.TAG_NAME, value='a')
        todaysMorningQuizUrl = linkToTodaysMorningQuiz.get_attribute('href')
        print("Following link to quiz: " + todaysMorningQuizUrl)
        driver.execute_script("arguments[0].scrollIntoView(true);", linkToTodaysMorningQuiz)
        linkToTodaysMorningQuiz.click()
        break
else :
    print("It doesn't look like a morning quiz has been published yet. Maybe try again later?")
    sys.exit()



## Section two - attempt the quiz:
quizContainer = driver.find_element(by=By.XPATH, value='//*[@id="content"]')
quizContainer1 = quizContainer.find_element(By.CLASS_NAME, "riddle-target-initialised")
quizIframeContainer = quizContainer1.find_element(By.TAG_NAME, "iframe")
driver.switch_to.frame(quizIframeContainer)

# Main question answering loop:
while True:
    # Because the questions are answered in a loop first we check if we're looking at a question or the results page:
    #question = driver.find_element(By.CLASS_NAME, "title").find_element(By.TAG_NAME, "h2")
    question = driver.find_elements(By.CSS_SELECTOR, '.title h2')
    if not question:
        # Didn't find the expected elements for a question so exiting loop now
        break
    print("Question: " + question[0].text)
    print("Multiple choice answers: ")
    answers = driver.find_element(By.CLASS_NAME, "choices").find_elements(By.CLASS_NAME, "choice")
    #answers = driver.find_element(By.CLASS_NAME, "choices").find_elements(By.CLASS_NAME, "choice-overlay")
    for a in answers:
        print("- " + a.find_element(By.CLASS_NAME, "choice-text").text)
    
    choosenAnswer = choice(answers)
    print("My answer is: " + choosenAnswer.find_element(By.CLASS_NAME, "choice-text").text)
    
    #How to click on the answer...
    #Scroll the answers into view so that click() works:
    driver.execute_script("arguments[0].scrollIntoView(true);", question[0])
    #manually wait after clicking, otherwise sometimes click doens't seem to register on the page (something is still loading?).
    time.sleep(2)
    #now click the answer:
    #choosenAnswer.find_element(By.CLASS_NAME, "choice-text").click()
    choosenAnswer.find_element(By.CLASS_NAME, "choice-overlay").click()
    
    # Wait for the result to the answer to be given....
    riddleContainer = driver.find_element(By.CLASS_NAME, "riddle-page")
    el = WebDriverWait(driver, timeout=10).until(lambda d: riddleContainer.find_element(By.CLASS_NAME, "choice-result").find_element(By.CLASS_NAME, "ng-binding"))
    print("This should show if your answer was right or worng:")
    print('"' + el.text + '"')
    
    # And now on to the next question:
    nextButton = riddleContainer.find_element(By.CLASS_NAME, "footer-content").find_element(By.TAG_NAME, "button")
    nextButton.click()


## Section three - Finished, show the score.
print("The quiz is finished.")
print("You scored: " + driver.find_element(By.CSS_SELECTOR, 'h1.result-score span b').text)

driver.quit()
