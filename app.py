"""Run: streamlit run app.py"""
import asyncio
import os
import streamlit as st
from lab_agents.agents import Assistant
from lab_agents.database import initialize

st.set_page_config(page_title='LabCare • Multi-Agent Demo',page_icon='🧪',layout='centered')
initialize()
st.title('🧪 LabCare')
st.caption('Multi-agent laboratory concierge | Arabic + English | FICTIONAL DATA ONLY')
st.warning('University demonstration. Not a medical service. Prices, slots and results are fictitious.')
if 'history' not in st.session_state:st.session_state.history=[]
model=os.getenv('OLLAMA_MODEL','qwen2.5:7b')
mode=st.sidebar.toggle('Use local Ollama for agent responses',value=True)
st.sidebar.caption('Switch off for deterministic offline testing (MCP still used).')
bot=Assistant(model=model,llm_enabled=mode)
for who,msg in st.session_state.history:
    with st.chat_message(who):st.write(msg)
q=st.chat_input('Ask about prices, hours, appointments, or results / اسأل عن الفحوصات')
if q:
    st.session_state.history.append(('user',q))
    with st.chat_message('user'):st.write(q)
    try:reply=asyncio.run(bot.chat(q))
    except Exception as ex:reply=f'Cannot reach MCP server: {type(ex).__name__}: {ex}'
    st.session_state.history.append(('assistant',reply))
    with st.chat_message('assistant'):st.write(reply)

with st.expander('📅 Book a demo appointment',expanded=False):
    if 'pending' not in st.session_state:st.session_state.pending=None
    try: sl=asyncio.run(bot.direct_tool('list_appointment_slots'))['slots']
    except Exception as ex:sl=[];st.error(f'MCP unavailable: {ex}')
    if sl:
        with st.form('book_prepare'):
            name=st.text_input('Your name (demo only)')
            code=st.selectbox('Test code', ['CBC','LIPID','TSH','VITD','FBS'])
            selected=st.selectbox('Available time',sl,format_func=lambda x:f"{x['day']} at {x['time']} ({x['remaining']} left)")
            prepare=st.form_submit_button('Review appointment')
        if prepare:st.session_state.pending={'slot_id':selected['id'],'customer_name':name,'test_code':code,'label':f"{name} · {code} · {selected['day']} {selected['time']}"}
    if st.session_state.pending:
        st.info('Please review: '+st.session_state.pending['label'])
        if st.button('Confirm demo booking',type='primary'):
            data=asyncio.run(bot.direct_tool('create_appointment',{**{k:v for k,v in st.session_state.pending.items() if k!='label'},'confirmed':True}))
            if data.get('ok'):st.success(f"Demo booking #{data['booking_id']} created.");st.session_state.pending=None
            else:st.error(data.get('error','Booking failed'))

with st.expander('🔐 Check a demo report',expanded=False):
    st.caption('Try DEMO-1001 / 472915 (released) or DEMO-1002 / 831264 (pending). Never use real identifiers.')
    with st.form('results'):
        report_id=st.text_input('Demo report ID')
        access_code=st.text_input('Private access code',type='password')
        check=st.form_submit_button('Check status')
    if check:
        data=asyncio.run(bot.direct_tool('get_report_status',{'report_id':report_id,'access_code':access_code}))
        if data.get('ok'):st.success(data.get('summary',data.get('message','Status retrieved')))
        else:st.error(data.get('error','Unable to retrieve result'))
