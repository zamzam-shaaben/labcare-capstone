"""Deterministic first-pass multilingual intent router."""
def heuristic_intent(s:str)->str:
    q=s.lower()
    if any(k in q for k in ('result','report','نتيجة','نتائج','فحصي','تحاليل')): return 'results'
    if any(k in q for k in ('book','appointment','reserve','موعد','احجز','حجز')):return 'booking'
    if any(k in q for k in ('price','cost','fee','سعر','أسعار','اسعار','بكم','تكلفة')):return 'prices'
    if any(k in q for k in ('hour','open','close','location','address','وقت','دوام','ساعات','عنوان','وين')):return 'hours'
    return 'general'
