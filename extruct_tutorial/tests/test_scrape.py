"""Validate JSON-LD Scrape outcome."""
import pytest
from extruct_tutorial import scrape


@pytest.fixture
def url():
    """Target URL to scrape metadata."""
    return 'https://hackersandslackers.com/creating-django-views/'


@pytest.fixture
def expected_json():
    """Expected metadata to be returned."""
    return {
        "@context": "https://schema.org/",
        "@type": "Article",
        "author": {
            "@type": "Person",
            "name": "Todd Birchard",
            "image": "https://cdn.hackersandslackers.com/2021/09/avimoji.jpg",
            "sameAs": "[\"https://toddbirchard.com\", \"https://twitter.com/toddrbirchard\", \"https://www.facebook.com/https://github.com/toddbirchard\"]"
        },
        "keywords": "Django, Python, Software",
        "headline": "Creating Interactive Views in Django",
        "url": "https://hackersandslackers.com/creating-django-views/",
        "datePublished": "2020-04-23T12:21:00.000-04:00",
        "dateModified": "2020-12-25T00:51:36.000-05:00",
        "image": {
            "@type": "ImageObject",
            "url": "https://cdn.hackersandslackers.com/2020/11/django-views.jpg",
            "width": 1000,
            "height": 523
        },
        "publisher": {
            "@type": "Organization",
            "name": "Hackers and Slackers",
            "logo": {
                "@type": "ImageObject",
                "url": "https://cdn.hackersandslackers.com/logo/logo.png",
                "width": 60,
                "height": 60
            }
        },
        "description": "Create interactive user experiences by writing Django views to handle dynamic content, submitting forms, and interacting with data.",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": "https://hackersandslackers.com"
        }
    }


def test_scrape(url, expected_json):
    """Match scrape's fetched metadata to known value."""
    metadata = scrape(url)
    assert metadata == expected_json
