from pathlib import Path
root = Path("public")
path = root / "app.js"
text = path.read_text()
assert "function obligationRow(o)" in text and "function obligations()" in text
text = text.replace("const DB='amwali_db_v1',KEY='data';", "const expandedObligations=new Set();const DB='amwali_db_v1',KEY='data';", 1)
start = text.index("function obligationRow(o)")
end = text.index("function flowRow(f)", start)
block = r'''function obligationRow(o){
const rem=remaining(o),paid=o.amount-rem,done=rem===0,progress=o.amount?Math.min(100,Math.max(0,paid*100/o.amount)):100;
const installments=state.payments.filter(p=>p.obligationId===o.id);
const expanded=expandedObligations.has(o.id);
const next=o.installment?Math.min(rem,o.installment):0;
const days=o.due?Math.round((new Date(o.due+'T12:00:00')-new Date(today()+'T12:00:00'))/86400000):null;
const relative=days===null?'غير محدد':days<0?'متأخر '+Math.abs(days)+' يوم':days===0?'اليوم':days===1?'غدًا':'بعد '+days+' يوم';
const details='<div class="fin-extra" id="fin-extra-'+e(o.id)+'" '+(expanded?'':'hidden')+'><div class="fin-metrics">'+
[['الرصيد المتبقي',money(rem)],['المبلغ الأصلي',money(o.amount)],['إجمالي المدفوع',money(paid)],['الدفعات المسجلة',String(installments.length)],['بداية الالتزام',dateLabel(o.start)],['تاريخ الاستحقاق المسجل',dateLabel(o.due)],['الجهة أو الشخص',e(o.party||'غير محددة')]].map(([k,v])=>'<div><small>'+k+'</small><strong>'+v+'</strong></div>').join('')+
'</div><div class="fin-progress-title"><span>تقدم السداد</span><strong>'+Math.round(progress)+'% · '+installments.length+' دفعة مسجلة</strong></div><div class="fin-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="'+Math.round(progress)+'" aria-label="تقدم السداد"><span style="width:'+progress+'%"></span></div><button class="tiny" data-action="details" data-id="'+e(o.id)+'">جميع التفاصيل وسجل السداد</button></div>';
return '<article class="fin-row"><div class="fin-head"><div class="fin-name"><h3>'+e(o.name)+'</h3><small>'+e(o.type||'التزام')+(done?' · مكتمل':'')+'</small></div><div class="fin-next"><small>'+(done?'الحالة':'الدفعة القادمة')+'</small><strong>'+(done?'مسدد':next?money(next):'غير محددة')+'</strong></div></div>'+
'<div class="fin-due"><span>الاستحقاق</span><strong>'+dateLabel(o.due)+'</strong><span class="'+(days!==null&&days<0&&!done?'fin-late':'')+'">'+(done?'مكتمل':relative)+'</span></div>'+
'<div class="fin-bottom"><div class="fin-rem"><small>المتبقي</small><strong>'+money(rem)+'</strong></div><div class="fin-actions"><button class="fin-toggle" data-action="toggle-obligation" data-id="'+e(o.id)+'" aria-expanded="'+expanded+'" aria-controls="fin-extra-'+e(o.id)+'">'+(expanded?'إخفاء':'التفاصيل')+'</button>'+(done?'':'<button class="fin-pay" data-action="pay" data-id="'+e(o.id)+'">سداد</button>')+'</div></div>'+details+'</article>';
}
function obligations(){
const active=state.obligations.filter(o=>remaining(o)>0);
const up=upcoming();
const due=up.reduce((n,o)=>n+(o.installment||remaining(o)),0);
return '<section class="fin-summary" aria-label="ملخص الالتزامات"><div><span>المستحق خلال 30 يومًا</span><strong>'+money(due)+'</strong><small>تقديري وفق المواعيد المسجلة</small></div><div><span>الالتزامات النشطة</span><strong>'+active.length+'</strong></div></section>'+
'<div class="section-head"><h2>الالتزامات ('+state.obligations.length+')</h2><button class="btn" data-action="add-obligation">+ التزام</button></div>'+
(state.obligations.length?'<div class="fin-list">'+[...state.obligations].sort((a,b)=>(a.due||'9999').localeCompare(b.due||'9999')).map(obligationRow).join('')+'</div>':'<div class="empty">لا توجد التزامات بعد. أضف قسطًا أو دينًا شخصيًا.</div>');
}
'''
text = text[:start] + block + text[end:]
assert "case 'choose':open('choose');break;" in text
text = text.replace("case 'choose':open('choose');break;", "case 'toggle-obligation':if(expandedObligations.has(identifier))expandedObligations.delete(identifier);else expandedObligations.add(identifier);render();break;case 'choose':open('choose');break;", 1)
path.write_text(text)
index = root / "index.html"
html = index.read_text()
assert '<link rel="stylesheet" href="styles.css"/>' in html
html = html.replace('<link rel="stylesheet" href="styles.css"/>', '<link rel="stylesheet" href="styles.css"/><link rel="stylesheet" href="smart-list.css"/>')
index.write_text(html)
(root / "smart-list.css").write_text(Path("refinement/smart-list.css").read_text())
sw = root / "sw.js"
sw_text = sw.read_text().replace("amwali-static-v2", "amwali-static-v4-smart-list")
sw_text = sw_text.replace("'./styles.css',", "'./styles.css', './smart-list.css',")
sw.write_text(sw_text)
print("Amwali smart list applied; persistent state and financial calculations unchanged")
