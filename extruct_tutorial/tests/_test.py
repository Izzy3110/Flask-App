import json

from extruct_tutorial import scrape


def url():
    """Target URL to scrape metadata."""
    return 'https://hackersandslackers.com/creating-django-views/'


with open("current.json", "w") as f:
    metadata = scrape(url())
    f.write(json.dumps(metadata, indent=4))
    # json.dump(f, metadata, indent=4)
    f.close()

