"""Run: python -m lab_agents.mcp_server (stdio MCP)."""
import json
from mcp.server.fastmcp import FastMCP
from . import service

server = FastMCP('fictional-laboratory')
@server.tool()
def get_test_prices(query:str='')->str:
    """Read catalog test prices and preparation information; empty query returns all."""
    return json.dumps(service.prices(query),ensure_ascii=False)
@server.tool()
def get_opening_hours()->str:
    """Get the fictional laboratory address and opening hours."""
    return json.dumps(service.hours())
@server.tool()
def list_appointment_slots()->str:
    """List demo booking slots and remaining availability."""
    return json.dumps(service.slots())
@server.tool()
def create_appointment(slot_id:int,customer_name:str,test_code:str,confirmed:bool=False)->str:
    """Book a DEMO appointment only after customer explicitly confirmed the summary."""
    return json.dumps(service.booking(slot_id,customer_name,test_code,confirmed))
@server.tool()
def get_report_status(report_id:str,access_code:str)->str:
    """Get demo laboratory report status using report ID AND private access code."""
    return json.dumps(service.result(report_id,access_code),ensure_ascii=False)
if __name__=='__main__':server.run(transport='stdio')
