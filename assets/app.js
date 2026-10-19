const $ = id => document.getElementById(id);
const token = document.querySelector('meta[name="app-token"]').content;
let lastKey = '';
let previousStatus = '';
let polling = false;
let autoStarted = false;
const number = value => Number(value).toFixed(6);
const config = {responsive:true, displaylogo:false, modeBarButtons:[["toImage"],["zoom2d","pan2d"],["zoomIn2d","zoomOut2d","autoScale2d","resetScale2d"]], scrollZoom:true, toImageButtonOptions:{format:'png',scale:2}};

async function action(path, body={}) {
    const response = await fetch(path, {method:'POST',headers:{'Content-Type':'application/json','X-App-Token':token},body:JSON.stringify(body)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Request failed');
    return data;
}

function plot(name, rows, runs) {
    const element = $('plot-'+name);
    element.hidden = !rows.length;
    if (!rows.length) return;
    const x = rows.map(r=>r.n);
    const traces = [];
    for (let i=0;i<runs;i++) traces.push({x,y:rows.map(r=>r.runs[i]),type:'scatter',mode:'markers',name:'Individual runs',legendgroup:'runs',showlegend:i===0,marker:{color:'#c3bdf5',size:7},hovertemplate:'n=%{x}<br>Estimate=%{y:.6f}<extra>Run '+(i+1)+'</extra>'});
    traces.push({x,y:rows.map(r=>r.mean),mode:'lines+markers',name:'Mean',line:{color:'#6457e7',width:2.5},marker:{size:6}});
    traces.push({x,y:rows.map(r=>r.reference),mode:'lines',name:'Theoretical',line:{color:'#d47b45',dash:'dash',width:1.5}});
    traces.push({x,y:rows.map(r=>r.error>0?r.error:null),xaxis:'x2',yaxis:'y2',mode:'lines+markers',name:'Absolute error',line:{color:'#6457e7',width:2}});
    traces.push({x,y:rows.map(r=>r.sd>0?r.sd:null),xaxis:'x2',yaxis:'y2',mode:'lines+markers',name:'Sample SD',line:{color:'#179b91',dash:'dash',width:2},marker:{symbol:'square',size:6}});
    const axis={type:'log',tickmode:'array',tickvals:x,ticktext:x.map(n=>n.toLocaleString('en-US')),gridcolor:'#eff1f6',zeroline:false,title:{text:'Sample size n',font:{size:10}}};
    const annotations=[{text:name==='pi'?'Pi estimates':'Euler’s number estimates',x:0,y:1.12,xref:'paper',yref:'paper',xanchor:'left',showarrow:false,font:{size:14,color:'#28273d'}},{text:'Accuracy & stability',x:.59,y:1.12,xref:'paper',yref:'paper',xanchor:'left',showarrow:false,font:{size:14,color:'#28273d'}}];
    if(rows.some(r=>r.error===0||r.sd===0)) annotations.push({text:'Zero values are omitted on the logarithmic axis.',x:1,y:-.26,xref:'paper',yref:'paper',showarrow:false,xanchor:'right',font:{size:9}});
    Plotly.react(element,traces,{margin:{l:52,r:15,t:80,b:55},paper_bgcolor:'#fff',plot_bgcolor:'#fff',font:{family:'Arial, sans-serif',size:10,color:'#687082'},xaxis:{...axis,domain:[0,.43]},xaxis2:{...axis,domain:[.59,1],anchor:'y2'},yaxis:{title:{text:'Estimate',font:{size:10}},gridcolor:'#eff1f6',zeroline:false},yaxis2:{anchor:'x2',type:'log',title:{text:'Magnitude (log)',font:{size:10}},gridcolor:'#eff1f6',zeroline:false},legend:{orientation:'h',y:1.32,x:0,font:{size:9}},annotations,uirevision:name},config);
}

function render(state) {
    const busy = state.status==='running';
    $('run').disabled=busy;
    $('stop').disabled=!busy;
    $('status').textContent=({ready:'Ready',running:'Simulation running',complete:'Complete',stopped:'Stopped · partial results',error:'Simulation failed'})[state.status];
    $('percent').textContent=Math.round(state.progress)+'%';
    $('progress').value=state.progress;
    if(state.error) $('error').textContent=state.error;
    const latest=state.logs.at(-1);
    $('run-detail').textContent=latest ? `${latest.experiment.toUpperCase()} · n=${latest.n.toLocaleString('en-US')} · run ${latest.run} · ${number(latest.estimate)}`:'Choose settings and run your first experiment.';
    const key=JSON.stringify(state.results);
    if(key!==lastKey) {
        lastKey=key;
        const results=state.results;
        for(const name of ['pi','e']) plot(name,results[name]||[],state.settings?.runs||5);
        const cards=[];
        for(const name of ['pi','e']) {
            const row=(results[name]||[]).at(-1);
            cards.push(`<div><small>${name==='pi'?'PI ESTIMATE':'EULER ESTIMATE'}</small><strong>${row?number(row.mean):'—'}</strong><em>${row?`n=${row.n.toLocaleString('en-US')} · error ${number(row.error)}`:'No complete sample group'}</em></div>`);
        }
        cards.push('<div><small>COMPLETED RUNS</small><strong id="run-count">0</strong><em>Independent replications</em></div>');
        $('metrics').innerHTML=cards.join('');
        const rows=[];
        for(const [name,groups] of Object.entries(results)) for(const row of groups) row.runs.forEach((value,i)=>rows.push(`<tr><td>${name==='pi'?'π':'e'}</td><td>${row.n.toLocaleString('en-US')}</td><td>${i+1}</td><td>${number(value)}</td><td>${number(row.mean)}</td><td>${number(row.error)}</td><td>${number(row.sd)}</td></tr>`));
        $('rows').innerHTML=rows.join('');
    }
    if($('run-count')) $('run-count').textContent=state.logs.length;
    $('logs').textContent=state.logs.length?state.logs.map(r=>`${r.experiment.toUpperCase().padEnd(3)}  n=${String(r.n).padEnd(8)}  run ${String(r.run).padEnd(3)}  estimate ${number(r.estimate)}`).join('\n'):'Waiting for a simulation.';
    if(previousStatus!==state.status) previousStatus=state.status;
}

async function refresh() {
    if(polling) return;
    polling=true;
    try {
        const response=await fetch('/api/state');
        if(!response.ok) throw new Error('Connection failed');
        const state=await response.json();
        render(state);
        if(!autoStarted && state.status==='ready') {autoStarted=true; $('settings').requestSubmit();}
    } catch(error) {
        $('error').textContent='Cannot reach the Python app. Restart odev.py and reopen its URL.';
    } finally { polling=false; }
}

$('settings').addEventListener('submit', async event=>{
    event.preventDefault();
    try {
        const sizes=$('sizes').value.split(',').map(s=>Number(s.trim()));
        await action('/api/start',{sizes,runs:Number($('runs').value),seed:Number($('seed').value),experiment:$('experiment').value});
        $('error').textContent='';
        lastKey='';
        await refresh();
    } catch(error) { $('error').textContent=error.message; }
});
$('stop').addEventListener('click',async()=>{try{await action('/api/stop');await refresh();}catch(error){$('error').textContent=error.message;}});
$('new-seed').addEventListener('click',()=>{$('seed').value=crypto.getRandomValues(new Uint32Array(1))[0];});
for(const button of document.querySelectorAll('[data-view]')) button.addEventListener('click',()=>{
    for(const tab of document.querySelectorAll('[data-view]')) tab.classList.toggle('active',tab===button);
    for(const view of document.querySelectorAll('.view')) view.hidden=view.id!==button.dataset.view;
    if(button.dataset.view==='charts') for(const id of ['plot-pi','plot-e']) if($(id).data) Plotly.Plots.resize(id);
});
refresh();
setInterval(refresh,400);
