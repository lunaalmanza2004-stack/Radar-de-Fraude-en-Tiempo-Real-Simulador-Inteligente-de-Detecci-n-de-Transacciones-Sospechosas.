let socket;
let paused = false;
const txBody = document.querySelector("#txTable tbody");
const alertBody = document.querySelector("#alertTable tbody");
const metricTotal = document.getElementById("metric-total");
const metricAlerts = document.getElementById("metric-alerts");
const metricLastMinute = document.getElementById("metric-last-minute");
const metricPrecision = document.getElementById("metric-precision");
const searchInput = document.getElementById("searchInput");

async function fetchMetrics(){
  const r = await fetch('/api/metrics');
  const m = await r.json();
  metricTotal.textContent = m.total;
  metricAlerts.textContent = m.alerts;
  metricLastMinute.textContent = m.last_minute;
  metricPrecision.textContent = m.precision_est.toFixed(3);
}

async function fetchInitialTables(){
  const [txsRes, alertsRes] = await Promise.all([
    fetch('/api/transactions?limit=100'),
    fetch('/api/alerts?limit=50')
  ]);
  const txs = await txsRes.json();
  const alerts = await alertsRes.json();
  txBody.innerHTML = '';
  alerts.forEach(addAlertRow);
  txs.forEach(addTxRow);
}

function addTxRow(t){
  if(!passesFilter(t)) return;
  const tr = document.createElement('tr');
  const badge = `<span class="badge ${t.level==='HIGH'?'high':t.level==='MEDIUM'?'med':'low'}">${t.level}</span>`;
  const date = new Date(t.ts*1000).toLocaleTimeString();
  tr.innerHTML = `
    <td>${t.id}</td>
    <td>${t.user_id}</td>
    <td>${t.country}</td>
    <td>${t.payment_method}</td>
    <td>${t.device}</td>
    <td>$${t.amount.toFixed(2)}</td>
    <td>${t.risk.toFixed(3)}</td>
    <td>${badge}</td>
    <td>${date}</td>
    <td><button class="btn btn-primary" onclick="explain(${t.id})">¿Por qué?</button></td>
  `;
  txBody.prepend(tr);
  while(txBody.children.length>200) txBody.removeChild(txBody.lastChild);
}

function addAlertRow(a){
  const date = new Date(a.ts*1000).toLocaleTimeString();
  let reasons = [];
  try{ reasons = JSON.parse(a.reasons); }catch(e){}
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>${a.id}</td>
    <td>${a.transaction_id}</}</td>
    <td><span class="badge ${a.level==='HIGH'?'high':'med'}">${a.level}</span></td>
    <td>${(reasons||[]).join(' · ')}</td>
    <td>${date}</td>
  `;
  alertBody.prepend(tr);
  while(alertBody.children.length>100) alertBody.removeChild(alertBody.lastChild);
}

function passesFilter(t){
  const q = (searchInput.value||'').trim().toLowerCase();
  if(!q) return true;
  const hay = `${t.country} ${t.payment_method} ${t.device} ${t.level}`.toLowerCase();
  return hay.includes(q);
}

function connectWS(){
  socket = new WebSocket((location.protocol=='https:'?'wss':'ws')+'://'+location.host+'/ws/stream');
  socket.addEventListener('message', (ev)=>{
    if(paused) return;
    try{
      const msg = JSON.parse(ev.data);
      if(msg.type==='transaction'){
        addTxRow(msg.data);
        if(msg.level!=='LOW'){
          addAlertRow({id:0, transaction_id:msg.data.id, level:msg.level, reasons:JSON.stringify(msg.reasons), ts:msg.data.ts});
        }
      }
    }catch(e){}
  });
  socket.addEventListener('close', ()=>{
    setTimeout(connectWS, 1500);
  });
}

async function explain(id){
  const out = document.getElementById('botOutput');
  out.textContent = 'Pensando...';
  const r = await fetch('/api/explain/'+id);
  const j = await r.json();
  if(j.ok){
    out.textContent = j.explanation;
  }else{
    out.textContent = 'No se encontró la transacción.';
  }
}

document.getElementById('explainBtn').addEventListener('click', ()=>{
  const id = parseInt(document.getElementById('txIdInput').value,10);
  if(!isNaN(id)) explain(id);
});

document.getElementById('pauseBtn').addEventListener('click', ()=> paused = true);
document.getElementById('resumeBtn').addEventListener('click', ()=> paused = false);

searchInput.addEventListener('input', async ()=>{
  const r = await fetch('/api/transactions?limit=100');
  const txs = await r.json();
  txBody.innerHTML = '';
  txs.forEach(addTxRow);
});

fetchMetrics();
fetchInitialTables();
setInterval(fetchMetrics, 3000);
connectWS();
