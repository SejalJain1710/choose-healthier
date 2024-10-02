import requests
import requests
import json
from pprint import pprint
from pymongo import MongoClient
from dotenv import load_dotenv
import os, uuid
from pymongo import UpdateOne


load_dotenv()
def connect_to_mongo():
    MONGO_URI = os.getenv('MONGO_URI')
    DATABASE_NAME = "scrapperDB"
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    return db


def scrape():
    url = 'https://api.tatadigital.com/api/v2/sso/check-session'

    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'access-control-allow-origin': 'https://api.tatadigital.com',
        'client_id': 'BIGBASKET-WEB-DESKTOP-APP',
        'content-type': 'application/json',
        'origin': 'https://www.bigbasket.com',
        'priority': 'u=1, i',
        'referer': 'https://www.bigbasket.com/',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    }

    payload = {
        "codeChallenge": "bbETbz-P9ym9Rdmn7rU5Q9oMW3gTQP3PYWQyK0FnbOg",
        "redirectUrl": "https://www.bigbasket.com/?nc=logo"
    }
    session = requests.Session()
    response = session.post(url, headers=headers, data=json.dumps(payload))

    for retry in range(5):
        if response.status_code == 200:
            break
        else:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
    responses = []
    url = 'https://www.bigbasket.com/listing-svc/v2/products?type=pc&slug=snacks-branded-foods'

    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'cookie': 'x-entry-context-id=100; x-entry-context=bb-b2c; _bb_locSrc=default; x-channel=web; _bb_loid=j:null; _bb_bhid=; _bb_nhid=1723; _bb_vid=Mzk4MTIwNDY4NTczNTI4MzAy; _bb_dsevid=; _bb_dsid=; _bb_cid=1; _bb_aid=MzA4NTgxODk5Nw==; _bb_home_cache=3308129e.1.visitor; _bb_bb2.0=1; is_global=1; _bb_addressinfo=; _bb_pin_code=; _bb_sa_ids=10654; _is_tobacco_enabled=0; _is_bb1.0_supported=0; _bb_cda_sa_info=djIuY2RhX3NhLjEwMC4xMDY1NA==; is_integrated_sa=0; bb2_enabled=true; jarvis-id=cda13a80-ad7f-4d31-89b2-facea896c31f;',
        'priority': 'u=1, i',
        'referer': 'https://www.bigbasket.com/cl/snacks-branded-foods/?nc=nb',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'x-channel': 'BB-WEB',
        'x-tracker': '57ac3a0c-4a2e-449a-86a6-623d6e1c70d5',
    }
    for page in range(1, 6):
        try:
            response = session.get(url, headers=headers, params={'page': page})
            responses.append(response)
        except Exception as e:
            print(e)
    
    for response in responses:
        if response.status_code == 200:
            data2 = response.json()
            products = data2.get('tabs')[0].get('product_info').get('products')
            final_data = []
            final_categories = []
            for product in products:
                try:
                    name = product.get('desc')
                    url = product.get('absolute_url')
                    price = product.get('pricing',{}).get('discount',{}).get('mrp', '-1')
                    images = product.get('images', [])
                    category = product.get('category').get('mlc_id', None)
                    category_name = product.get('category').get('mlc_name', None)
                    brand = product.get('brand').get('name', 'No Brand')
                    qty = product.get('w', '0')
                    local_data = {
                        '_id': url,
                        'price': price,
                        'images': images,
                        'category': category,
                        'brand': brand,
                        'name': name,
                        'qty': qty
                    }
                    final_data.append(local_data)
                    final_categories.append({'_id': category, 'name': category_name})
                except Exception as e:
                    print(e)
                
            db = connect_to_mongo()
            product_collection = db['products']
            category_collection = db['categories']
            
            if final_data:
                product_operations = [
                    UpdateOne({'_id': item['_id']}, {"$set": item}, upsert=True) for item in final_data
                ]
                product_collection.bulk_write(product_operations)

            if final_categories:
                category_operations = [
                    UpdateOne({'_id': item['_id']}, {"$set": item}, upsert=True) for item in final_categories
                ]
                category_collection.bulk_write(category_operations)
        else:
            print(f"Failed to retrieve data: {response.status_code}")


if __name__ == '__main__':
    scrape()