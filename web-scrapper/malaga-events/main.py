import requests
from bs4 import BeautifulSoup
import json
import time

base_url = "https://www.malaga.eu"
list_url = base_url + "/la-ciudad/agenda/index.html?mas=true&pageNum="
events = []

try:
    soup = BeautifulSoup(requests.get(list_url + "1").text, 'html.parser')
    last_page_link = soup.select_one("a.lastpagelink.pagelink")
    last_page = int(last_page_link['href'].split('pageNum=')[1]) if last_page_link else 6
except:
    last_page = 6

for page in range(1, last_page + 1):
    print(f"Scraping page {page} of {last_page}")
    try:
        soup = BeautifulSoup(requests.get(list_url + str(page)).text, 'html.parser')

        for event in soup.select(".listado-agenda .list .list-element"):
            try:
                title_link = event.select_one(".title-element a")
                title = title_link.text.strip()
                detail_url = base_url + title_link['href']
                date_times = event.select(".date-element time")
                place = event.select_one(".place-element span:nth-of-type(2)").text.strip()
                description = event.select_one(".description p").text.strip()

                event_data = {
                    "event": title,
                    "date": {
                        "from": date_times[0].get("datetime") if date_times else "",
                        "to": date_times[1].get("datetime") if len(date_times) > 1 else ""
                    },
                    "place": place,
                    "description": description,
                    "details": {}
                }

                try:
                    detail_page = BeautifulSoup(requests.get(detail_url).text, 'html.parser')
                    info_section = detail_page.select_one("dl.dl-horizontal.dl-basic")

                    if info_section:
                        dt_tags = info_section.find_all("dt")
                        dd_tags = info_section.find_all("dd")

                        for i in range(len(dt_tags)):
                            try:
                                if i < len(dd_tags):
                                    key = dt_tags[i].text.strip().rstrip(":").lower()
                                    value = dd_tags[i].get_text(strip=True, separator=" ")
                                    event_data["details"][key] = value

                                    times = dd_tags[i].select("time")
                                    if times and len(times) > 0:
                                        date_values = []
                                        for time_tag in times:
                                            date_values.append(time_tag.get("datetime", ""))
                                        if date_values:
                                            event_data["details"][key + "_dates"] = date_values
                            except:
                                pass
                except:
                    pass

                events.append(event_data)
                time.sleep(0.5)
            except Exception as e:
                print(f"Error processing event: {e}")
    except Exception as e:
        print(f"Error processing page {page}: {e}")

with open('malaga_events.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, ensure_ascii=False, indent=2)
