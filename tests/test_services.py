import pytest
from lab_agents import database,service
from lab_agents.routing import heuristic_intent

@pytest.fixture(autouse=True)
def fresh_db(tmp_path,monkeypatch):
    monkeypatch.setattr(database,'DB',tmp_path/'lab.sqlite3')
    database.initialize()

def test_catalog():
    assert len(service.prices()['items'])==5
    assert service.prices('TSH')['items'][0]['price_usd']==18

def test_hours():assert service.hours()['hours']['Sunday']=='Closed'

def test_slots():assert len(service.slots()['slots'])==5

def test_requires_confirmation():
    assert not service.booking(1,'Demo Tester','CBC',False)['ok']
    assert service.slots()['slots'][0]['remaining']==2

def test_book_capacity():
    assert service.booking(1,'Demo Tester','CBC',True)['ok']
    assert service.booking(1,'Demo Tester Two','CBC',True)['ok']
    assert not service.booking(1,'Demo Third','CBC',True)['ok']

def test_invalid_booking():
    assert not service.booking(99,'Demo Tester','CBC',True)['ok']
    assert not service.booking(1,'D','CBC',True)['ok']
    assert not service.booking(1,'Demo Tester','NONEXISTENT',True)['ok']

def test_result_protected():
    assert not service.result('DEMO-1001','bad')['ok']
    assert service.result('DEMO-1002','831264')['status']=='pending'
    assert service.result('DEMO-1001','472915')['status']=='released'

def test_intents():
    for question,expected in [('how much price?','prices'),('شو أوقات الدوام؟','hours'),('book appointment','booking'),('نتائج الفحوصات','results')]:
        assert heuristic_intent(question)==expected
