from bs4 import BeautifulSoup as bs
from timeit import default_timer as timer
import re
import requests
import sqlite3

def get_darwin_laptops(db, cursor, url, page_num_class):
    resp = requests.get(f'{url}1')
    soup = bs(resp.text, "html.parser")
    product_specs = []
    all_products_specs = []
    try:
        pages_num = int(soup.select(f'.{page_num_class}')[-1].text)//7
    except:
        pages_num = int(soup.select(f'.{page_num_class}')[-2].text)//7
    print(pages_num)
    for page in range(1, pages_num+1):
        new_url = f'{url}{page}'
        resp = requests.get(new_url)
        soup = bs(resp.text, "html.parser")

        product_raw_titles = soup.find_all('h3', class_='title')
        product_prices = soup.find_all('span', attrs={"class": ["price-new"]})
        image_link = soup.find_all('img', class_='card-image')
        product_descrs = []
        product_titles = []

        for i in range(len(product_raw_titles)):
            product_raw_descr = product_raw_titles[i].find('span')
            if '|' in product_raw_descr.text:
                product_descr = []
                temp_descr = product_raw_descr.text.split('|')
                if 'TB' in temp_descr[2]:
                    temp_descr[2] = str(int(temp_descr[2].replace('TB', '').strip()) * 1024)
                product_descr.append(temp_descr[3].strip())
                product_descr.append(temp_descr[4].strip())
                product_descr.append(temp_descr[1].strip())
                product_descr.append(temp_descr[2].strip())
                product_titles.append(product_raw_titles[i].find('a'))
                product_descrs.append(product_descr)
            else:
                continue

        for i in range(len(product_descrs)):
            image_url = image_link[i].get('src')
            image_response = requests.get(image_url)
            with open(f"static/imgs/{product_titles[i].text}.jpg", "wb") as f:
                f.write(image_response.content)
            specs = {
                'TITLE': product_titles[i].text,
                'PRICE': product_prices[i].text.replace(" ", "").replace("lei", ""),
                'PROCESSOR': product_descrs[i][0].strip(),
                'VIDEO-CARD': product_descrs[i][1],
                'RAM': product_descrs[i][2].replace('GB', '').replace('TB', '').strip(),
                'MEMORY': product_descrs[i][3].replace('GB', '').replace('TB', '').strip(),
                'LINK': product_titles[i].get('href'),
                'SOURCE': 'DARWIN.MD'
            }
            product_specs.append(specs)
        print(f'Page {page} processed!')
    all_products_specs += product_specs

    # ---- Remove duplicates ----------
    seen = set()
    result = []
    for d in all_products_specs:
        h = d.copy()
        h.pop('LINK')
        h = tuple(h.items())
        if h not in seen:
            result.append(d)
            seen.add(h)

    all_products_specs = result
    # -------------------------------
    for specs in all_products_specs:
        # ----- Add to BD -----
        print(f"""
                    'INSERT INTO laptops (title, price, processor, video_card, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                '{specs['PROCESSOR']}', '{specs['VIDEO-CARD']}', {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}')'""")
        cursor.execute(
            f"""INSERT INTO laptops (title, price, processor, video_card, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                '{specs['PROCESSOR']}', '{specs['VIDEO-CARD']}', {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}');
                                                """)
        db.commit()


def get_bomba_laptops(db, cursor, url, page_num_class):
    resp = requests.get(f'{url}1')
    soup = bs(resp.text, "html.parser")
    product_specs = []
    all_products_specs = []
    try:
        pages_num = int(soup.select(f'.{page_num_class}')[-1].text)
    except:
        pages_num = int(soup.select(f'.{page_num_class}')[-2].text)
    print(pages_num)
    for page in range(1, pages_num+1):
        new_url = f'{url}{page}'
        resp = requests.get(new_url)
        soup = bs(resp.text, "html.parser")

        product_titles = soup.select('.product-name')
        product_descr = []
        for i in range(len(product_titles)):
            if ', ' in product_titles:
                product_descr.append(product_titles[i].text.split(', '))
        for i in range(len(product_descr)):
            product_descr[i][0] = product_descr[i][0].replace("\nLaptop/Notebook", "").strip()
            if not (' GB' in product_descr[i][1]):
                product_descr[i].pop(1)
            if 'TB' in product_descr[i][2]:
                product_descr[i][2] = str(int(product_descr[i][2].replace('TB', '').strip()) * 1024)

        main_product_prices = soup.select(f'.{"aac-price-main"}')
        new_product_prices = soup.select(f'.{"aac-price-new"}')
        product_prices = main_product_prices + new_product_prices
        image_link = soup.find_all('img', attrs={'width': '292'})
        new_image_link = []
        print(image_link)
        for i in range(len(image_link)):
            print(image_link[i])
            try:
                link = image_link[i].get('data-lazy')
                if 'version_8/1.jpg' in link:
                    new_image_link.append(link)
            except:
                pass
        image_link = new_image_link

        for i in range(len(product_descr)):
            if product_titles[i].find('a').get('href')[0] == '/':
                link = "http://" + re.findall(r"://(.*.md)/", url)[0] + product_titles[i].find('a').get('href')
            else:
                link = "http://" + product_titles[i].find('a').get('href')
            resp_new = requests.get(link)
            soup_new = bs(resp_new.text, "html.parser")
            temp_descr = soup_new.select('.characteristicstd1')
            processor = ''
            video_card = ''
            for j in range(len(temp_descr)):
                if 'Procesor' in temp_descr[j].text:
                    processor = soup_new.select('.characteristicstd2')[j].text
                if 'Modelul placii video' in temp_descr[j].text:
                    video_card = soup_new.select('.characteristicstd2')[j].text
            try:
                image_url = "http://bomba.md" + image_link[i]
                print(image_url)
                image_response = requests.get(image_url)
                with open(f"static/imgs/{product_descr[i][0]}.jpg", "wb") as f:
                    f.write(image_response.content)
            except: pass

            specs = {
                'TITLE': product_descr[i][0],
                'PRICE': product_prices[i].text.replace(" ", "").replace("MDL", ""),
                'PROCESSOR': processor,
                'VIDEO-CARD': video_card,
                'RAM': product_descr[i][1].replace('GB', '').replace('TB', '').strip(),
                'MEMORY': product_descr[i][2].replace('GB', '').replace('TB', '').strip(),
                'LINK': link,
                'SOURCE': 'BOMBA.MD'
            }
            product_specs.append(specs)
            print(product_descr)
        print(f'Page {page} processed!')
    all_products_specs += product_specs

    # ---- Remove duplicates ----------
    seen = set()
    result = []
    for d in all_products_specs:
        h = d.copy()
        h.pop('LINK')
        h = tuple(h.items())
        if h not in seen:
            result.append(d)
            seen.add(h)

    all_products_specs = result
    # -------------------------------
    for specs in all_products_specs:
        # ----- Add to BD -----
        print(f"""
                    'INSERT INTO laptops (title, price, processor, video_card, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                '{specs['PROCESSOR']}', '{specs['VIDEO-CARD']}', {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}')'""")
        cursor.execute(
            f"""INSERT INTO laptops (title, price, processor, video_card, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                '{specs['PROCESSOR']}', '{specs['VIDEO-CARD']}', {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}');
                                                """)
        db.commit()


def get_enter_laptops(db, cursor, url, page_num_class):
    resp = requests.get(f'{url}1')
    soup = bs(resp.text, "html.parser")
    product_specs = []
    all_products_specs = []
    try:
        pages_num = int(soup.select(f'.{page_num_class}')[-1].text)
    except:
        pages_num = int(soup.select(f'.{page_num_class}')[-2].text)
    print(pages_num)
    for page in range(1, pages_num+1):
        new_url = f'{url}{page}'
        resp = requests.get(new_url)
        soup = bs(resp.text, "html.parser")

        product_titles = soup.find_all('span', class_='product-title')
        product_descr = soup.find_all('span', class_='product-descr')
        product_prices = soup.find_all('span', attrs={"class": ["price", "price-new"]})
        image_link = soup.find_all('span', class_='loading-img')

        for i in range(len(product_descr)):
            image_url = image_link[i].find('img').get('data-src')
            image_response = requests.get(image_url)
            specs_temp =  product_descr[i].text.split('/ ')
            if not('GB' in specs_temp[1]):
                specs_temp[0] += specs_temp[1]
                specs_temp.pop(1)
            if not('VGA' in specs_temp[3]) and not('GeForce' in specs_temp[3]) and not('Intel' in specs_temp[3]):
                specs_temp[3] = ''
            if 'TB' in specs_temp[2]:
                specs_temp[2] = str(int(specs_temp[2].replace('TB', '').strip()) * 1024)
            with open(f"static/imgs/{product_titles[i].text}.jpg", "wb") as f:
                f.write(image_response.content)
            specs = {
                'TITLE': product_titles[i].text,
                'PRICE': product_prices[i].text.replace(" ", "").replace("lei", ""),
                'PROCESSOR': specs_temp[0].strip(),
                'VIDEO-CARD': specs_temp[3],
                'RAM': specs_temp[1].replace('GB', '').replace('TB', '').strip(),
                'MEMORY': specs_temp[2].replace('GB', '').replace('TB', '').strip(),
                'LINK': product_titles[i].find_parent('a').get('href'),
                'SOURCE': 'ENTER.online'
            }
            product_specs.append(specs)
        print(f'Page {page} processed!')
    all_products_specs += product_specs

    # ---- Remove duplicates ----------
    seen = set()
    result = []
    for d in all_products_specs:
        h = d.copy()
        h.pop('LINK')
        h = tuple(h.items())
        if h not in seen:
            result.append(d)
            seen.add(h)

    all_products_specs = result
    # -------------------------------
    for specs in all_products_specs:
        # ----- Add to BD -----
        print(f"""
                    'INSERT INTO laptops (title, price, processor, video_card, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                '{specs['PROCESSOR']}', '{specs['VIDEO-CARD']}', {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}')'""")
        cursor.execute(
            f"""INSERT INTO laptops (title, price, processor, video_card, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                '{specs['PROCESSOR']}', '{specs['VIDEO-CARD']}', {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}');
                                                """)
        db.commit()


def get_darwin_phones(db, cursor, url, page_num_class):
    resp = requests.get(f'{url}1')
    soup = bs(resp.text, "html.parser")
    product_specs = []
    all_product_specs = []
    try:
        pages_num = int(soup.select(f'.{page_num_class}')[-1].text)//3
    except:
        pages_num = int(soup.select(f'.{page_num_class}')[-2].text)//3

    for page in range(1, pages_num):
        new_url = f'{url}{page}'
        resp = requests.get(new_url)
        soup = bs(resp.text, "html.parser")

        product_titles = soup.find_all('h3', class_='title')
        product_descr = soup.find_all('h3', class_='title')
        product_prices = soup.find_all('span', attrs={"class": ["price-new"]})
        image_link = soup.find_all('img', class_='card-image')

        for i in range(len(product_descr)):
            try:
                image_url = image_link[i].get('src')
                image_response = requests.get(image_url)
                product_title = product_titles[i].find('a').text.split(re.findall(r'\d* GB', product_descr[i].find('a').text)[0])[0].strip()
                with open(f"static/imgs/{product_title}.jpg", "wb") as f:
                    f.write(image_response.content)
                descr = product_descr[i].find("span")
                print(product_descr[i].text)
                ram = re.findall(r"\d* GB", descr.text)[0].replace(" GB", "").strip()
                specs = {
                    'TITLE': product_title,
                    'PRICE': product_prices[i].text.replace(" ", "").replace("lei", ""),
                    'RAM': ram,
                    'MEMORY': re.findall(r"\d* GB", product_descr[i].find('a').text)[0].replace(" GB", ""),
                    'LINK': product_titles[i].find('a').get('href'),
                    'SOURCE': 'DARWIN.MD'
                }
                if int(specs['MEMORY']) > 10:
                    product_specs.append(specs)
            except:
                pass
        print(f'Page {page} processed!')
    all_product_specs += product_specs
    print(all_product_specs)

    # ---- Remove duplicates ----------
    seen = set()
    result = []
    for d in all_product_specs:
        h = d.copy()
        h.pop('LINK')
        h = tuple(h.items())
        if h not in seen:
            result.append(d)
            seen.add(h)

    all_products_specs = result

    print(all_product_specs)
    # -------------------------------

    for specs in all_products_specs:
        # ----- Add to BD -----
        print(f"""
                    'INSERT INTO phones (title, price, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}')'""")
        cursor.execute(
            f"""INSERT INTO phones (title, price, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}');
                                                """)
        db.commit()


def get_enter_phones(db, cursor, url, page_num_class):
    resp = requests.get(f'{url}1')
    soup = bs(resp.text, "html.parser")
    product_specs = []
    all_product_specs = []
    try:
        pages_num = int(soup.select(f'.{page_num_class}')[-1].text)
    except:
        pages_num = int(soup.select(f'.{page_num_class}')[-2].text)

    for page in range(1, pages_num):
        new_url = f'{url}{page}'
        resp = requests.get(new_url)
        soup = bs(resp.text, "html.parser")

        product_titles = soup.find_all('span', class_='product-title')
        product_descr = soup.find_all('span', class_='product-descr')
        product_prices = soup.find_all('span', attrs={"class": ["price", "price-new"]})
        image_link = soup.find_all('span', class_='loading-img')

        for i in range(len(product_descr)):
            ram = int(re.findall(r"\d\d*\s", product_descr[i].text)[0].strip())
            if ram < 10:
                ram *= 1024
            image_url = image_link[i].find('img').get('data-src')
            image_response = requests.get(image_url)
            with open(f"static/imgs/{product_titles[i].text}.jpg", "wb") as f:
                f.write(image_response.content)
            specs = {
                'TITLE': product_titles[i].text,
                'PRICE': product_prices[i].text.replace(" ", "").replace("lei", ""),
                'RAM': str(ram),
                'MEMORY': re.findall(r"\d\d*\s", product_descr[i].text)[1].strip(),
                'LINK': product_titles[i].find_parent('a').get('href'),
                'SOURCE': 'ENTER.online'
            }
            product_specs.append(specs)
        print(f'Page {page} processed!')
    all_product_specs += product_specs

    # ---- Remove duplicates ----------
    seen = set()
    result = []
    for d in all_product_specs:
        h = d.copy()
        h.pop('LINK')
        h = tuple(h.items())
        if h not in seen:
            result.append(d)
            seen.add(h)

    all_products_specs = result
    # -------------------------------

    for specs in all_products_specs:
        # ----- Add to BD -----
        print(f"""
                    'INSERT INTO phones (title, price, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}')'""")
        cursor.execute(
            f"""INSERT INTO phones (title, price, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                                {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}');
                                                """)
        db.commit()


def get_bomba_phones(db,cursor, url, title_class, main_price_class, price_new_class, currency_str, page_num_class):
    resp = requests.get(f'{url}1')
    soup = bs(resp.text, "html.parser")

    try:
        pages_num = int(soup.select(f'.{page_num_class}')[-1].text)
    except:
        pages_num = int(soup.select(f'.{page_num_class}')[-2].text)
    all_products_specs = []
    for page in range(pages_num):
        new_url = f'{url}{page}'
        resp = requests.get(new_url)
        soup = bs(resp.text, "html.parser")
        product_specs = []
        product_titles_raw = soup.select(f'.{title_class}')
        product_titles = []
        main_product_prices = soup.select(f'.{main_price_class}')
        new_product_prices = soup.select(f'.{price_new_class}')
        product_prices = main_product_prices + new_product_prices
        image_link = soup.find_all('img', attrs={'width': '292'})
        new_image_link = []
        for i in range(len(image_link)):
            link = image_link[i].get('data-lazy')
            if 'version_8/1.jpg' in link:
                new_image_link.append(image_link[i].get('data-lazy'))
            print(new_image_link)
        image_link = new_image_link
        print(str(image_link))
        all_specs = []
        for i in range(len(product_titles_raw)):
            product_title = ""
            link = ""
            if product_titles_raw[i].find('a').get('href')[0] == '/':
                link = "http://" + re.findall(r"://(.*.md)/", url)[0] + product_titles_raw[i].find('a').get('href')
            else:
                link = "http://" + product_titles_raw[i].find('a').get('href')
            if len(re.findall(r" \d*GB/\d*GB", product_titles_raw[i].text)) == 1:
                specs = {
                    'TITLE': product_titles_raw[i].text.split(re.findall(r"\d*GB/\d*GB", product_titles_raw[i].text)[0])[0].strip().replace("Telefon mobil ", "").replace("Smartphone ", ""),
                    'PRICE': product_prices[i].text.replace(" ", "").replace(currency_str, ""),
                    'RAM': re.findall(r"\d*GB/\d*GB", product_titles_raw[i].text)[0].split('/')[0].replace("GB", ""),
                    'MEMORY': re.findall(r"\d*GB/\d*GB", product_titles_raw[i].text)[0].split('/')[1].replace("GB", ""),
                    'LINK': link,
                    'SOURCE': 'BOMBA.MD'
                }
                product_specs.append(specs)
            elif len(re.findall(r" \d*GB/ \d*GB", product_titles_raw[i].text)) == 1:
                specs = {
                    'TITLE': product_titles_raw[i].text.split(re.findall(r"\d*GB/ \d*GB", product_titles_raw[i].text)[0])[0].strip().replace("Telefon mobil ", "").replace("Smartphone ", ""),
                    'PRICE': product_prices[i].text.replace(" ", "").replace(currency_str, ""),
                    'RAM': re.findall(r"\d*GB/ \d*GB", product_titles_raw[i].text)[0].split('/')[0].replace("GB", ""),
                    'MEMORY': re.findall(r"\d*GB/ \d*GB", product_titles_raw[i].text)[0].split('/')[1].replace("GB", ""),
                    'LINK': link,
                    'SOURCE': 'BOMBA.MD'
                }
                product_specs.append(specs)
            elif len(re.findall(r" \d*/\d*", product_titles_raw[i].text)) == 1:
                specs = {
                    'TITLE': product_titles_raw[i].text.split(re.findall(r" \d*/\d*", product_titles_raw[i].text)[0])[0].strip().replace("Telefon mobil ", "").replace("Smartphone ", ""),
                    'PRICE': product_prices[i].text.replace(" ", "").replace(currency_str, ""),
                    'RAM': re.findall(r" \d*/\d*", product_titles_raw[i].text)[0].split('/')[0],
                    'MEMORY': re.findall(r" \d*/\d*", product_titles_raw[i].text)[0].split('/')[1],
                    'LINK': link,
                    'SOURCE': 'BOMBA.MD'
                }
                product_specs.append(specs)
            elif len(re.findall(r" \d*GB", product_titles_raw[i].text)) == 1:
                specs = {
                    'TITLE': product_titles_raw[i].text.split(re.findall(r"\d*GB", product_titles_raw[i].text)[0])[0].strip().replace("Telefon mobil ", "").replace("Smartphone ", ""),
                    'PRICE': product_prices[i].text.replace(" ", "").replace(currency_str, ""),
                    'RAM': 404,
                    'MEMORY': re.findall(r"\d*GB", product_titles_raw[i].text)[0].replace("GB", ""),
                    'LINK': link,
                    'SOURCE': 'BOMBA.MD'
                }
                product_specs.append(specs)
            elif len(re.findall(r" \d*GB", product_titles_raw[i].text)) == 2:
                specs = {
                    'TITLE': product_titles_raw[i].text.split(re.findall(r"\d*GB", product_titles_raw[i].text)[0])[0].strip().replace("Telefon mobil ", "").replace("Smartphone ", ""),
                    'PRICE': product_prices[i].text.replace(" ", "").replace(currency_str, ""),
                    'RAM': re.findall(r"\d*GB", product_titles_raw[i].text)[0].replace("GB", ""),
                    'MEMORY': re.findall(r"\d*GB", product_titles_raw[i].text)[1].replace("GB", ""),
                    'LINK': link,
                    'SOURCE': 'BOMBA.MD'
                }
                product_specs.append(specs)
            else:
                specs = {
                    'TITLE': product_titles_raw[i].text.strip().replace("Telefon mobil ", "").replace("Smartphone ", ""),
                    'PRICE': product_prices[i].text.replace(" ", "").replace(currency_str, ""),
                    'RAM': 404,
                    'MEMORY': 404,
                    'LINK': link,
                    'SOURCE': 'BOMBA.MD'
                }
                product_specs.append(specs)
            product_title = specs["TITLE"]
            try:
                image_url = "http://bomba.md" + image_link[i]
                print(image_url)
                image_response = requests.get(image_url)
                with open(f"static/imgs/{product_title}.jpg", "wb") as f:
                    f.write(image_response.content)
            except:
                pass

            print(len(product_specs))

            all_products_specs += product_specs

    # ---- Remove duplicates ----------
    seen = set()
    result = []
    for d in all_products_specs:
        h = d.copy()
        h.pop('LINK')
        h = tuple(h.items())
        if h not in seen:
            result.append(d)
            seen.add(h)

    all_products_specs = result
    # -------------------------------

    for specs in all_products_specs:
        # ----- Add to BD -----
        print(f"""
            'INSERT INTO phones (title, price, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                        {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}')'""")
        cursor.execute(
            f"""INSERT INTO phones (title, price, ram, memory, link, source) VALUES ('{specs['TITLE']}', {specs['PRICE']},
                                        {specs['RAM']}, {specs['MEMORY']}, '{specs['LINK']}', '{specs['SOURCE']}');
                                        """)
        db.commit()


def get_phones():
    start = timer()
    URLs = {'Enter': 'https://enter.online/telefoane/smartphone-uri?filter=873-1&page=',
            'Bomba': 'https://www.bomba.md/ro/category/gsm-tv-electrocasnice-gsm-tablete-gsm/?&page=',
            'Darwin': 'https://darwin.md/telefoane?page='}

    f = open('data.txt', 'w')
    db = sqlite3.connect("products.db")
    cursor = db.cursor()
    try:
        cursor.execute("""DROP TABLE phones""")
    except:
        pass
    try:
        cursor.execute("""CREATE TABLE phones (
                        title text,
                        price integer,
                        ram integer,
                        memory integer,
                        link text,
                        source text
                        )
                        """)
        db.commit()
    except:
        pass

    get_bomba_phones(db, cursor, URLs["Bomba"], "product-name", "aac-price-main", "aac-price-new", "MDL", "p-numbers")
    get_enter_phones(db, cursor, URLs["Enter"], "page-link")
    get_darwin_phones(db, cursor, URLs["Darwin"], 'page-link')


    f.close()
    end = timer()
    f.close()

    print(f"Elapsed {end-start} seconds!")


def get_laptops():
    start = timer()

    URLs = {'Enter': 'https://enter.online/laptopuri?filter=873-1&page=',
            'Bomba': 'https://www.bomba.md/ro/category/laptopuri-si-echipamente-it-echipamente-it-toate-notebook-urile/?&page=',
            'Darwin': 'https://darwin.md/laptopuri?page='}

    f = open('data.txt', 'w')
    db = sqlite3.connect("products.db")
    cursor = db.cursor()
    try:
        cursor.execute("""DROP TABLE laptops""")
        print("REMOVED TABLE")
    except:
        pass
    try:
        cursor.execute("""CREATE TABLE laptops (
                            title text,
                            price integer,
                            processor text,
                            video_card text,
                            ram integer,
                            memory integer,
                            link text,
                            source text
                            )
                            """)
        print("CREATED TABLE")
        db.commit()
    except:
        pass

    get_enter_laptops(db, cursor, URLs['Enter'], 'page-link')
    get_bomba_laptops(db, cursor, URLs['Bomba'], 'p-numbers')
    get_darwin_laptops(db, cursor, URLs['Darwin'], 'page-link')

get_laptops()
get_phones()
