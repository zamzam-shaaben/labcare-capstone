"""Deterministic first-pass multilingual intent router."""
FOLLOW_UPS=('and ','what about','how about','also ','same for','و','ماذا عن','كمان','طيب')

def heuristic_intent(s:str)->str:
    q=s.lower()
    if any(k in q for k in ('result','report','نتيجة','نتائج','فحصي','تحاليل')): return 'results'
    if any(k in q for k in ('book','appointment','reserve','موعد','احجز','حجز')):return 'booking'
    if any(k in q for k in ('price','cost','fee','how much','سعر','أسعار','اسعار','بكم','قديش','تكلفة')):return 'prices'
    if any(k in q for k in ('hour','open','close','location','address','وقت','دوام','ساعات','عنوان','وين')):return 'hours'
    return 'general'

def route(message:str,history=())->str:
    """Heuristic intent, with short follow-ups ("and TSH?") inheriting the topic of the previous user turn."""
    intent=heuristic_intent(message)
    if intent!='general':return intent
    q=message.strip().lower()
    if len(q.split())<=6 and q.startswith(FOLLOW_UPS):
        for who,text in reversed(list(history)):
            if who=='user' and heuristic_intent(text)!='general':return heuristic_intent(text)
    return 'general'
