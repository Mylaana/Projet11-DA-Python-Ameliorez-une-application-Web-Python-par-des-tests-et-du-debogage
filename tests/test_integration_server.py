"""testing load_clubs and load_competition integration with other functions"""
from unittest.mock import patch
from flask import url_for
import server
from .fixtures import app, captured_template, client, revert_competitions_json, revert_clubs_json


def test_showsummary(client, captured_template):
    data = {"email": "john@simplylift.co"}
    response = client.post("/showSummary", data=data)
    template, context = captured_template[0]
    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "welcome.html"
    assert context['club']['name'] == 'Simply Lift'
    assert context['competitions'][0]['name'] == 'Spring Festival'

def test_book_past_competition(client, captured_template):
    response = client.get("book/Spring Festival/Simply Lift")
    template, context = captured_template[0]

    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "welcome.html"

def test_purchase_places(client, captured_template, revert_competitions_json, revert_clubs_json):
    club = ["Simply Lift"]
    competition = ["Spring Festival"]
    places_before = 25
    places_bought = 3
    data = {"club": club, "competition": competition, "places": places_bought}

    response = client.post("/purchasePlaces", data=data)
    expected_value = places_before - places_bought

    template, context = captured_template[0]
    assert response.status_code == 200
    assert str(expected_value) == str(context['competitions'][0]['numberOfPlaces'])
    assert template.name == 'welcome.html'
