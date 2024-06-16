import requests
import json
from bs4 import BeautifulSoup
import pickle

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

def get_cinema_names(url):
    all_info = {}
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    all_cinemas = [i.text for i in soup.find_all("div", class_="cinemaList_name")]
    all_ref_cinemas = [i.get("href") for i in soup.find_all("a", class_="cinemaList_ref")]
    for i in range(len(all_cinemas)):
        all_info[all_cinemas[i]] = all_ref_cinemas[i]
    return all_info

def get_info_about_cinema(url):
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')

    cinema_name = soup.find("h1", class_="universalHat_title").text.replace('\xa0', '')
    cinema_addr = soup.find("span", class_="theaterInfo_dataAddr").text.replace('\xa0', '')
    phone_number = soup.find("p", class_="theaterInfo_phoneNumber").text.replace('\xa0', '') if soup.find("p",
                                                                        class_="theaterInfo_phoneNumber") else "Нет информации"
    cinema_picture = soup.find(class_="universalHat_logo picture")
    if cinema_picture!=None:
        cinema_picture = cinema_picture.find("source").get("srcset")
    else:
        cinema_picture = None
    all_info = {
        "Название кинотеатра": cinema_name,
        "Адрес кинотеатра": cinema_addr,
        "Номер телефона": phone_number,
        "Картинка": cinema_picture,
        "Отзывы": f"{url}/comments/"
    }
    return all_info

def get_info_about_films(url):
    url = f"{url}schedule/"
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    all_info = {}
    films = [i.text for i in soup.find_all("span", class_="showtimesMovie_name")]
    film_categories = [i.text for i in soup.find_all("span", class_="showtimesMovie_categories")]
    film_details = [i.text for i in soup.find_all("span", class_="showtimesMovie_details")]
    film_formats = [i.text for i in soup.find_all("span", class_="showtimes_format")]
    film_time_sessions = [[j.text for j in i.find_all("span", class_="session_time")] for i in soup.find_all("div",
                                                                                            class_="showtimes_sessions")]
    film_price_sessions = [[j.text for j in i.find_all("span", class_="session_price")] for i in soup.find_all("div",
                                                                                            class_="showtimes_sessions")]
    for i in range(len(films)):
        film_specs = {"categories": film_categories[i],
                      "details": film_details[i],
                      "formats": film_formats[i],
                      "time_sessions": film_time_sessions[i],
                      "price_sessions": film_price_sessions[i]}
                     # "film_trailer": film_trailer_links[i]}
        all_info[films[i]] = film_specs
    json_data = json.dumps(all_info, ensure_ascii=False, indent=4)
    with open('all_info.json', 'w', encoding='utf-8') as file:
        file.write(json_data)
    return all_info


def get_all_theaters(url):
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    ref_all_cinemas = soup.find_all("a", class_="cinemaList_ref")
    cinema_links = [item.get("href") for item in ref_all_cinemas]
    cinema_films = [get_films(item) for item in cinema_links]
    cinema_names = [get_cinema_name(item) for item in cinema_links]
    all_info = {}
    for i in range(len(cinema_names)):
        value = {}
        value["link"] = cinema_links[i]
        value["films"] = cinema_films[i]
        all_info[cinema_names[i]] = value
    return all_info


def get_all_films(url):
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    ref_all_cinemas = soup.find_all("a", class_="cinemaList_ref")
    cinema_links = [item.get("href") for item in ref_all_cinemas]
    all_films = [film for sublist in [get_films(item) for item in cinema_links] for film in sublist]
    all_films = list(set(all_films))
    with open('all_films.pkl', 'wb') as f:
        pickle.dump(all_films, f)
    return list(set(all_films))

def get_films(url):
    url = f"{url}schedule/"
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    films = [i.text for i in soup.find_all("span", class_="showtimesMovie_name")]
    return films


def get_cinema_name(url):
    req = requests.get(url, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    cinema_name = soup.find("h1", class_="universalHat_title").text.replace('\xa0', '')
    return cinema_name