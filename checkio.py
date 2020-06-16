import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException,ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from dataclasses import dataclass
import time


def read_credentials():
    secrets = "secrets.json"
    with open(secrets) as f:
        keys = json.loads(f.read())
        return keys

@dataclass
class Task:
    title: str
    task_link: str


class CheckIOSolver:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.google = "https://www.google.com/"
        self.base_url = "https://checkio.org/"
        self.home_url = "https://py.checkio.org/"
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.implicitly_wait(50) # Set impicit waits for 50 seconds
        self.SEARCH_TEXT = "Python checkIO "
        self.opened_station_list = []
        self.task_ToSolve_List = []
        self.chekio_mainpage_url = ""
        self.current_solvingTask_url = ""
        self.current_google_result_link =[]
        self.curr_google_solution_code = []

    def login_to_checkio(self):
        self.driver.get(self.base_url)
        self.driver.maximize_window()
        self.get_on_python_checkio()
        self.put_credentials_to_form()
        self.chekio_mainpage_url = self.driver.current_url

    def put_credentials_to_form(self):
        try:
            # Enter user credentials and Submit the form
            self.driver.find_element_by_id("id_username").send_keys(self.login)
            time.sleep(1)
            password_field = self.driver.find_element_by_id("id_password")
            password_field.send_keys(self.password)
            password_field.submit()
            time.sleep(1)
        except NoSuchElementException:
            print("Exception NoSuchElementException")

    def get_on_python_checkio(self):
        try:
            self.driver.find_element_by_link_text('Python').click()
            time.sleep(2)
        except NoSuchElementException:
            print("incorrect Page")


    def get_all_opened_stations(self):
        if self.driver.current_url != self.chekio_mainpage_url:
            self.driver.get(self.chekio_mainpage_url)
        opened_stations = self.driver.find_elements_by_class_name("map__station_state_opened")
        print("Total Number of Opened Stations = {}".format(len(opened_stations)))
        self.opened_station_list = [station.find_element_by_css_selector('a').get_attribute("href") for station in opened_stations]
        print(self.opened_station_list)

    def get_all_tasks_in_station(self, station_link):
        self.driver.get(station_link)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        tasks = soup.find_all(class_='island-tasks__container')
        self.task_ToSolve_List = []
        for task in tasks:
            task_status_element = task.find(class_='island-tasks__side__sign')
            if task_status_element:
                task_status = task_status_element.get('title')
            else:
                task_status = "Haven't Seen"
            if task_status != 'Solved':
                title = task.find(class_='island-tasks__task__title').get('title')
                link = self.home_url + task.find('a').get('href')
                self.task_ToSolve_List.append(Task(title, link))
        print(self.task_ToSolve_List)

    def navigate_to_taskSolvepage(self,task):
        print("Navigate to Task -> " + task.title)
        print(task.task_link)
        self.driver.get(task.task_link)
        time.sleep(2)
        print("Click on Solve It button")
        try:
            solveit_link = self.driver.find_element_by_xpath("//a[@class='btn']").click()
        except ElementClickInterceptedException:
            print("--- Pop up Appeared ----")
            self.driver.find_element_by_xpath("//div[@class='congratulation__body__accept']").click()
            print("--- Closed Popup ---")
            time.sleep(2)
            solveit_link = self.driver.find_element_by_xpath("//a[@class='btn']").click()
        time.sleep(2)
        self.current_solvingTask_url = self.driver.current_url
        print("\nCurrent Task's Solving Page, URL -> " + self.current_solvingTask_url)


    def get_google_search_result(self,task):
        #Navigate to Google.com and enter the Search text "Python checkIO {TASK NAME}"
        print("Google Search: Task - " + task.title + "\n")
        self.driver.get(self.google)
        time.sleep(2)
        searchbox = self.driver.find_element_by_name("q")
        searchbox.send_keys(self.SEARCH_TEXT + task.title)
        time.sleep(1)
        searchbox.submit()
        time.sleep(2)

        google_results = self.driver.find_elements_by_xpath("//div[@class='r']/a[contains(@href,'publications')]")
        self.current_google_result_link = []
        for results in google_results:
            self.current_google_result_link.append(results.get_attribute("href"))
        time.sleep(3)
        print(self.current_google_result_link)

    def get_solution_code(self, google_result_link):
        print("\nGet Googled Solution --- ")
        self.driver.get(google_result_link)
        time.sleep(2)
        publications_code = self.driver.find_element_by_xpath("//div[@class='publications__info__code']")
        solution_code = publications_code.find_elements_by_xpath("//span[@style='padding-right: 0.1px;']")
        self.curr_google_solution_code = []
        for data in solution_code:
            code_words = data.find_elements_by_css_selector('span')
            code_line = ""
            for word in code_words:
                code_line += word.text
            print(code_line)
            if len(code_line) > 0: self.curr_google_solution_code.append(code_line)


    def check_current_solution(self,task):
        print("\nPaste the Code and Check Solution for Task - " + task.title)
        self.driver.get(self.current_solvingTask_url)
        solution_textarea_element = self.driver.find_element_by_xpath("//textarea")
        solution_textarea_element.send_keys(Keys.CONTROL + "a")
        solution_textarea_element.send_keys(Keys.DELETE)
        time.sleep(1)

        for i in self.curr_google_solution_code:
            solution_textarea_element.send_keys(i)
            solution_textarea_element.send_keys('\n')
            solution_textarea_element.send_keys(Keys.HOME)
        time.sleep(2)

        self.driver.find_element_by_id('check-code-btnEl').click()
        time.sleep(6)
        success_element = self.driver.find_elements_by_xpath("//div[@class='animation-success']")
        if len(success_element)>0:
            print("SUCCESS!!! Completed Task -: " + task.title)
            return True
        else:
            print("Failed Task -: " +  task.title)
            return False

    def solve_current_task(self,task):
        for result_link in self.current_google_result_link:
            self.get_solution_code(result_link)
            if self.check_current_solution(task): break

    def solve_all_tasks_in_station(self):
        for task in self.task_ToSolve_List:
            print("Solve Task - " + task.title)
            self.get_google_search_result(task)
            self.navigate_to_taskSolvepage(task)
            self.solve_current_task(task)

    def solve_missions(self):
        self.get_all_opened_stations()
        for link in self.opened_station_list:
            self.get_all_tasks_in_station(link)
            self.solve_all_tasks_in_station()

    def main_logic(self):
        self.login_to_checkio()
        for i in range(10):
            self.solve_missions()

        time.sleep(3)
        self.driver.quit()

if __name__ == '__main__':
    credentials = read_credentials()
    bot = CheckIOSolver(credentials['username'], credentials['password'])
    bot.main_logic()
