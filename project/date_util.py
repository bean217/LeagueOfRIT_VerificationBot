import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime


def get_classes_startdate():
    try:
        res = requests.get("https://www.rit.edu/calendar")
        data = res.text.lower()
        soup = BeautifulSoup(data, 'html.parser')
        fall_sem_tree = [s for s in soup.find_all('thead') if re.search("fall semester", s.text)][0]
        fs_child = fall_sem_tree.find_next_sibling('tbody')
        date_neighbor = [s for s in fs_child.find_all('td') if re.search("day, evening, and online classes begin", s.text)][0]
        start_date = date_neighbor.find_previous_sibling('td').text
        return datetime.strptime(start_date, "%B %d, %Y (%A)")
    except:
        # if scraping doesn't work
        # use August 28th of the previous year if current month < May
        if datetime.now().month < 5:
            return datetime.strptime(f"08/28/{datetime.now().year-1}", "%m/%d/%Y")
        # use August 28th of the current year if current month >= May
        else:
            return datetime.strptime(f"08/28/{datetime.now().year}", "%m/%d/%Y")