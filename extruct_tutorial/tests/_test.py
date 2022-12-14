import json
import os
import time
import uuid
from extruct_tutorial import scrape


scrapes = {}


def get_json(url):
    global scrapes
    time_start = time.time()
    metadata = scrape(url)
    time_end = time.time()
    scrape_uuid = str(uuid.uuid4())
    time_str = str(time.time())
    json_data = {
        "uuid": scrape_uuid,
        "url": url,
        "scrape_json": metadata,
        "elapsed": time_end - time_start
    }
    scrapes[time_str] = json_data
    with open(os.path.join("data", "test-"+str(scrape_uuid)+".json"), "w") as test_json_f:
        test_json_f.write(json.dumps(json_data, indent=4))
        test_json_f.close()
    return json.dumps(json_data)


if __name__ == '__main__':
    test_url = 'https://hackersandslackers.com/creating-django-views/'
    json_ = get_json(url=test_url)
