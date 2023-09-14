import server
import pytest
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
    return server.app

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
