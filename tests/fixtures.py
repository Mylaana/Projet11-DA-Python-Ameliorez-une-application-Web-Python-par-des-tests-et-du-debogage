import server
import pytest
import json
from flask import template_rendered

"""
pytest usage + decorator exemple :

@pytest.mark.parametrize("inp1, inp2, exp", [[2, 3, "positive"]])
def test_return_value(inp1, inp2, exp):
    assert module.function(inp1, inp2) == exp

option :
app.config['TESTING']=True
"""

@pytest.fixture
def app():
    app = server.app
    # adding configuration for testing purpose, providing app and server info for app_context
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    app.config['TESTING'] = True
    return app

@pytest.fixture
def captured_template(app):
    """
    yields a tuple corresponding to the captured template and context
    """
    recorded = []

    def record(sender, template, context, **kwargs):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

@pytest.fixture
def client(app):
    yield app.test_client()

@pytest.fixture
def revert_competitions_json():
    # saving competitions JSON state before test
    competitions = server.loadCompetitions(True)
    
    yield

    # reverting competitions JSON to before test state
    with open('competitions.json', 'w') as file:
        json.dump(competitions, file, indent=4)

@pytest.fixture
def revert_clubs_json():
    # saving clubs JSON state before test
    clubs = server.loadClubs(True)
    
    yield

    # reverting clubs JSON to before test state
    with open('clubs.json', 'w') as file:
        json.dump(clubs, file, indent=4)