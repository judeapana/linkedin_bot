import csv
import os
import traceback

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class Bot:
    LINKED_IN = "https://www.linkedin.com/login"
    home = None
    search_to_list = None

    def __init__(self, _driver, wait=100):
        self._driver = _driver
        self.wait = wait

    @staticmethod
    def fdate(date):
        start = None
        end = None
        if '·' in date:
            date_str = date.split('·')
            if len(date_str) >= 0:
                end_start_str = date_str[0].split('-')
                if len(end_start_str) >= 0:
                    start = end_start_str[0]
                if len(end_start_str) >= 1:
                    end = end_start_str[1]
            return start, end

        else:
            date_str = date.split('-')
            if len(date_str) >= 0:
                start = date_str[0]
            if len(date_str) >= 1:
                end = date_str[1]
            return start, end

    def login(self, _username, _password, endpoint=LINKED_IN):
        try:
            self._driver.get(endpoint)
            username = self._driver.find_element(By.ID, 'username')
            username.send_keys(_username)
            password = self._driver.find_element(By.ID, 'password')
            password.send_keys(_password)
            password.send_keys(Keys.RETURN)
            return self._driver
        except Exception as e:
            traceback.print_exc()

    def check_element(self, current_driver, *args, **kwargs):
        try:
            return current_driver.find_element(*args, **kwargs)
        except AttributeError as e:
            return None
        except Exception as e:
            return None

    def check_elements(self, current_driver, *args, **kwargs):
        try:
            return current_driver.find_elements(*args, **kwargs)
        except AttributeError as e:
            return None
        except Exception as e:
            return None

    def search(self, param: str):
        try:
            element_present = expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[aria-label="Search"]'))
            WebDriverWait(self._driver, self.wait).until(element_present)
            searchbtn = self._driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Search"]')
            searchbtn.clear()
            searchbtn.send_keys(param)
            searchbtn.send_keys(Keys.RETURN)
            element_present = expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[aria-label="Companies"]'))
            WebDriverWait(self._driver, self.wait).until(element_present)
            self.check_element(self._driver, By.CSS_SELECTOR, 'button[aria-label="Companies"]').click()

            element_present = expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'app-aware-link'))
            WebDriverWait(self._driver, self.wait).until(element_present)
            res = self.check_elements(self._driver, By.XPATH,
                                      '/html/body/div[6]/div[3]/div/div[2]/div/div[1]/main/div/div/div[1]/ul/li')
            self.search_to_list = list(map(
                lambda x: self.check_element(x[1], By.XPATH,
                                             f'//li[{x[0] + 1}]/div/div/div[2]/div[1]/div[1]/div/span/span/a').text,
                enumerate(res)))

            return res

        except Exception as e:
            traceback.print_exc()

    def _make_files(self, company_name, data):
        directory_name = data.get('name').replace('/', '-')
        current_dir = os.getcwd()
        path = os.path.join(current_dir, company_name, directory_name)
        if not os.path.exists(path):
            os.mkdir(path)

        with open(os.path.join(current_dir, company_name, 'output.csv'), '+a') as f:
            w = csv.DictWriter(f, fieldnames=['name', 'url', 'bio', 'location'])
            r = data.copy()
            r.pop('info')
            w.writerow(r)
            f.close()

        with open(os.path.join(path, 'experience.csv'), 'w') as f:
            w = csv.DictWriter(f, fieldnames=['position', 'company', 'company_url', 'location', 'start',
                                              'end', 'detail'])
            w.writeheader()
            if data['info']['exp']:
                w.writerows(data['info']['exp'])
            f.close()

        with open(os.path.join(path, 'projects.csv'), 'w') as f:
            w = csv.DictWriter(f, fieldnames=['project', 'project_url', 'detail', 'start', 'end'])
            w.writeheader()
            if data['info']['pro']:
                w.writerows(data['info']['pro'])
            f.close()
        with open(os.path.join(path, 'education.csv'), 'w') as f:
            w = csv.DictWriter(f, fieldnames=['college', 'college_url', 'degree', 'start', 'end',
                                              'detail'])
            w.writeheader()
            if data['info']['educ']:
                w.writerows(data['info']['educ'])
            f.close()

    def _employees_retrievable(self):
        element_present = expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, 'a[class="app-aware-link"]'))
        WebDriverWait(self._driver, self.wait).until(element_present)

        current_employees = set([i.get_attribute('href') for i in
                                 self.check_elements(self._driver, By.CSS_SELECTOR,
                                                     'a[class="app-aware-link"]')])
        self.home = self._driver.current_url
        return current_employees

    def _project_retrievable(self, profile):
        projs = []
        try:
            self._driver.get(profile + 'details/projects/')
            self._driver.implicitly_wait(2)
            found = self.check_element(self._driver, By.CSS_SELECTOR, '.artdeco-empty-state__message')
            if not found:
                element_present = expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'ul.pvs-list'))
                WebDriverWait(self._driver, self.wait).until(element_present)
                e = self.check_elements(self._driver, By.CSS_SELECTOR,
                                        '.pvs-list__container ul.pvs-list li.pvs-list__item--line-separated')
                for index, i in enumerate(e, start=1):
                    project_name = self.check_element(i, By.XPATH,
                                                      f'//li[{index}]/div/div[2]/div[1]/div[1]/div/span/span[1]')

                    date = self.check_element(i, By.XPATH,
                                              f'//li[{index}]/div/div[2]/div[1]/div[1]/span/span[1]')

                    details = self.check_element(i, By.XPATH, f"//li[{index}]/div/div/div/span[1]")

                    project_link = self.check_element(i, By.XPATH,
                                                      f'//li[{index}]/div/div[2]/div[2]/ul/li[2]/div/a').get_attribute(
                        'href')

                    projects_data = {
                        'project': project_name.text if project_name else '',
                        'project_url': project_link.text if project_link else '',
                        'detail': details.text if details else '',
                        'start': self.fdate(date.text)[0] if date else '',
                        'end': self.fdate(date.text)[1] if date else ''
                    }
                    projs.append(projects_data)
                return projs
            else:
                return None
        except Exception as e:
            traceback.print_exc()
            pass

    def _experience_retrievable(self, profile, ):
        exps = []
        try:
            self._driver.get(profile + 'details/experience/')
            element_present = expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, 'ul.pvs-list'))
            WebDriverWait(self._driver, self.wait).until(element_present)
            e = self.check_elements(self._driver, By.CSS_SELECTOR,
                                    '.pvs-list__container ul.pvs-list li.pvs-list__item--line-separated')

            for index, i in enumerate(e, start=1):
                position = self.check_element(i, By.XPATH,
                                              f'//li[{index}]/div/div[2]/div[1]/div[1]/div/span/span[1]')
                company = self.check_element(i, By.XPATH,
                                             f'//li[{index}]/div/div[2]/div/div[1]/span[1]/span[1]')
                date = self.check_element(i, By.XPATH,
                                          f'//li[{index}]/div/div[2]/div/div[1]/span[2]/span[1]')
                details = self.check_element(i, By.XPATH,
                                             f'//li[{index}]/div/div[2]/div[2]/ul/li/div/ul/li/div/div/div/span[1]')
                company_url = self.check_element(i, By.XPATH, f'//li[{index}]/div/div[1]/a').get_attribute(
                    'href')

                _location = self.check_element(i, By.XPATH,
                                               f'//li[{index}]/div/div[2]/div[1]/div[1]/span[3]/span[1]')
                exp_data = {'position': position.text if position else '',
                            'company': company.text if company else '',
                            'company_url': company_url if company_url else '',
                            'location': _location.text if _location else '',
                            'start': self.fdate(date.text)[0] if date else '',
                            'end': self.fdate(date.text)[1] if date else '',
                            'detail': details.text if details else ''}
                exps.append(exp_data)
            return exps

        except Exception as e:
            traceback.print_exc()
            print(e)

    def _education_retrievable(self, profile):
        edus = []
        try:
            self._driver.get(profile + 'details/education/')
            self._driver.implicitly_wait(2)
            found = self.check_element(self._driver, By.CSS_SELECTOR, '.artdeco-empty-state__message')
            if not found:
                element_present = expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'ul.pvs-list'))
                WebDriverWait(self._driver, self.wait).until(element_present)
                e = self.check_elements(self._driver, By.CSS_SELECTOR,
                                        '.pvs-list__container ul.pvs-list li.pvs-list__item--line-separated')
                for index, i in enumerate(e, start=1):
                    college = self.check_element(i, By.XPATH,
                                                 f'//li[{index}]/div/div[2]/div[1]/a/div/span/span[1]')

                    degree = self.check_element(i, By.XPATH,
                                                f'//li[{index}]/div/div[2]/div[1]/a/span[1]/span[1]')

                    date = self.check_element(i, By.XPATH,
                                              f'//li[{index}]/div/div[2]/div[1]/a/span[2]/span[1]')
                    details = self.check_element(i, By.XPATH,
                                                 f'//li[{index}]/div/div[2]/div[2]/ul/li[1]/div/div/div/div/div/span[1]')

                    college_link = self.check_element(i, By.XPATH,
                                                      f'//li[{index}]/div/div[1]/a').get_attribute(
                        'href')

                    education_data = {
                        'college': college.text if college else '',
                        'college_url': college_link if college_link else '',
                        'degree': degree.text if degree else '',
                        'start': self.fdate(date.text)[0] if date else '',
                        'end': self.fdate(date.text)[1] if date else '',
                        'detail': details.text if details else ''}
                    edus.append(education_data)
                return edus
            else:
                return None
            # empty education
        except Exception:
            traceback.print_exc()
            pass

    def exec(self, company: WebElement):
        try:
            company = self.check_element(company, By.XPATH, '//div/div/div[2]/div[1]/div[1]/div/span/span/a')
            company_name = company.text.replace('/', '-')
            company.click()
            # click show employees
            element_present = expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[class="ember-view"]'))
            WebDriverWait(self._driver, self.wait).until(element_present)

            self.check_element(self._driver, By.CSS_SELECTOR, 'a[class="ember-view"]').click()
            if not os.path.exists(company_name):
                os.mkdir(company_name)
            with open(os.path.join(os.getcwd(), company_name, 'output.csv'), 'w') as f:
                file = csv.writer(f)
                file.writerow(['name', 'url', 'bio', 'location'])

            while True:
                # grab employees
                for i in self._employees_retrievable():
                    data = {
                        'name': '', 'url': '', 'bio': '', 'location': '', 'info': {
                            'exp': [],
                            'educ': [],
                            'pro': []}
                    }
                    if 'headless' in i:
                        continue
                    self._driver.get(i)
                    element_present = expected_conditions.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div .text-body-medium'))
                    WebDriverWait(self._driver, self.wait).until(element_present)
                    # profile
                    bio = self.check_element(self._driver, By.CSS_SELECTOR, 'div.text-body-medium').text
                    name = self.check_element(self._driver, By.CSS_SELECTOR, 'h1.break-words').text
                    location = self.check_element(self._driver, By.CSS_SELECTOR, 'span.inline.t-black--light').text
                    profile = self._driver.current_url

                    data['name'] = name
                    data['url'] = profile
                    data['bio'] = bio
                    data['location'] = location

                    self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    # experience
                    exp_data = self._experience_retrievable(profile)
                    data['info']['exp'] = exp_data
                    # projects
                    projs = self._project_retrievable(profile)

                    data['info']['pro'] = projs

                    # education
                    edus = self._education_retrievable(profile)
                    data['info']['educ'] = edus
                    self._make_files(company_name, data)

                self._driver.get(self.home)
                element_present = expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'button[aria-label="Next"]'))

                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(self._driver, self.wait).until(element_present)

                next_btn = self._driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Next"]')
                if next_btn.is_enabled():
                    next_btn.click()
                else:
                    self._driver.quit()
                    break
        except Exception as e:
            traceback.print_exc()


if __name__ == "__main__":
    PATH = 'drivers/geckodriver.exe'
    driver = webdriver.Firefox(executable_path=PATH)

    bot = Bot(driver)
    bot.login(_username=os.environ.get('_USERNAME'), _password=os.environ.get('_PASSWORD'))
    search = bot.search("Unacademy")
    bot.exec(search[0])
