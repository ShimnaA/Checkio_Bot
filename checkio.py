import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time


def read_credentials():
    secrets = "secrets.json"
    with open(secrets) as f:
        keys = json.loads(f.read())
        return keys

#Class Task contains the details of the Task.
class Task:
    def __init__(self, title, task_link, side_sign):
      self.title = title
      self.task_link = task_link
      self.side_sign = side_sign  # whether the task status is Solved/Haven't seen

    def __str__(self):
        return 'Task(title= '+self.title+' , task_link = '+str(self.task_link)+' , side_sign = '+str(self.side_sign)+')'

class CheckIOSolver:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.google = "https://www.google.com/"
        self.base_url = "https://checkio.org/"
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.implicitly_wait(50) # Set impicit waits for 50 seconds
        self.SEARCH_TEXT = "Python checkIO "
        self.all_station_list = []
        self.opened_station_list = []
        self.solved_station_list =[]
        self.total_stations = 0
        self.visited_station_count = 0
        self.task_ToSolve_List = []
        self.chekio_mainpage_url = ""
        self.current_solvingTask_url = ""

    def login_to_checkio(self):
        self.driver.get(self.base_url)
        self.get_on_python_checkio()
        self.put_credentials_to_form()

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

    def get_all_stations(self):
        all_stations =  self.driver.find_elements_by_xpath("//div[contains(@class,'map__station')]")
        self.total_stations = len(all_stations)
        print("Total Number of Stations " + str(self.total_stations))
        for station in all_stations:
            station_link = station.find_element_by_css_selector('a.map__station__link').get_attribute("href")
            print(station_link)
            self.all_station_list.append(station_link)
        self.chekio_mainpage_url = self.driver.current_url
        print(self.chekio_mainpage_url)

    def get_all_opened_stations(self):
        if self.driver.current_url != self.chekio_mainpage_url:
            self.driver.get(self.chekio_mainpage_url)
        opened_stations = self.driver.find_elements_by_xpath("//div[contains(@class,'map__station_state_opened')]")
        print("Total Number of Opened Stations " + str(len(opened_stations)))
        self.opened_station_list = []
        for station in opened_stations:
            open_station_link = station.find_element_by_css_selector('a.map__station__link').get_attribute("href")
            print(open_station_link)
            self.opened_station_list.append(open_station_link)

    def get_all_tasks_in_station(self, station_link):
        self.driver.get(station_link)
        time.sleep(5)
        task_elements = self.driver.find_elements_by_xpath("//div[@class='island-tasks__container__column island-tasks__info']")
        print("Total Number of Tasks = " + str(len(task_elements)) + " in station " + station_link)
        self.task_ToSolve_List = []
        for task_element in task_elements:
            try:
                task_element_summary = task_element.find_element_by_class_name('island-tasks__task__summary')
                task_link = task_element_summary.find_element_by_css_selector('a').get_attribute("href")
                title = task_element_summary.find_element_by_css_selector('span').get_attribute("title")
                side_sign = "Haven't seen"
                task_data = Task(title, task_link, side_sign)
                self.task_ToSolve_List.append(task_data)
            except NoSuchElementException:
                print("No Such Element Exception")

    def navigate_to_taskSolvepage(self,task):
        print("Navigate to Task - " + task.title)
        self.driver.get(task.task_link)
        time.sleep(2)
        print("Click on SolveIt button")
        solveit_link = self.driver.find_element_by_xpath("//a[@class='btn']").click()
        time.sleep(2)
        self.current_solvingTask_url = self.driver.current_url

    def get_google_search_result(self,task):
        #Navigate to Google.com and enter the Search text "Python checkIO {TASK NAME}"
        self.driver.get(self.google)
        time.sleep(2)
        searchbox = self.driver.find_element_by_name("q")
        searchbox.send_keys(self.SEARCH_TEXT + task.title)
        time.sleep(1)
        searchbox.submit()

        #driver.find_elements_by_xpath("//input[@value='Google Search']")[1].click()
        time.sleep(2)


    def solve_all_tasks_in_station(self):
        for task in self.task_ToSolve_List:
            self.navigate_to_taskSolvepage(task)
            self.get_google_search_result(task)


    def get_all_missions(self):
        self.get_all_opened_stations()
        for link in self.opened_station_list:
            self.get_all_tasks_in_station(link)
            self.solve_all_tasks_in_station()

    def solve_missions(self):
        #To make sure all the stations get covered (Can be replaced by while true)
        # Loops until count of stations visited (visited_station_count) is > total number of stations(24))
        self.get_all_stations()
        for i in range(self.total_stations):
            self.get_all_missions()




    def main_logic(self):
        self.login_to_checkio()
        self.solve_missions()



        time.sleep(3)
        self.driver.quit()


if __name__ == '__main__':
    credentials = read_credentials()
    bot = CheckIOSolver(credentials['username'], credentials['password'])
    bot.main_logic()
