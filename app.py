# pip install Flask requests beautifulsoup4 APScheduler pytz

from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

app = Flask(__name__)

# Initial empty list for storing IP addresses
ip_addresses = []

def fetch_ips():
    global ip_addresses
    # Website URL
    url = "https://www.cisco.com/c/en/us/support/docs/security/sourcefire-amp-appliances/118121-technote-sourcefire-00.html"

    # Send a GET request
    response = requests.get(url)

    # Temporary list to store the fetched IP addresses
    new_ip_addresses = []

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the webpage
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all tables with class 'sptable' and select the 9th one (index 8)
        ip_tables = soup.find_all('table', class_='sptable')
        if len(ip_tables) >= 9:
            ip_table = ip_tables[8]

            # Find the fourth <td> section and extract the IP addresses
            td_elements = ip_table.find_all('td')
            if len(td_elements) >= 4:
                fourth_td = td_elements[3]
                for p_tag in fourth_td.find_all('p'):
                    # IP addresses are separated by <br/> tags, so we split the text using <br/>
                    new_ip_addresses.extend(p_tag.stripped_strings)
                
    # Update the global IP addresses list
    ip_addresses = new_ip_addresses

# Fetch IPs initially before starting the application
fetch_ips()

# Set up the scheduler to fetch IPs daily at 10 am CST
scheduler = BackgroundScheduler()
trigger = CronTrigger(hour=10, minute=0, second=0, timezone=pytz.timezone('America/Chicago'))
scheduler.add_job(fetch_ips, trigger)
scheduler.start()

@app.route('/')
def index():
    # Render the webpage with the list of IP addresses
    return render_template_string('''
        {% for ip in ip_addresses %}
            {{ ip }}<br>
        {% endfor %}
    ''', ip_addresses=ip_addresses)

if __name__ == '__main__':
    
    # Start the Flask application
    app.run(debug=True)