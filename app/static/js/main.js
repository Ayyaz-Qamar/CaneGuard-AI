const TX = {
  en: {
    analyzing:"Analyzing image...", processing:"Analyzing video...",
    detecting:"Detecting location...", noFile:"Please select a file first.",
    confidence:"Confidence", disease:"Disease", damage:"Leaf Damage",
    severity:"Severity", treatment:"Treatment Recommendations",
    fungicide:"Fungicide / Spray", fertilizer:"Fertilizer",
    precautions:"Precautions", weatherAdv:"Weather Risk Advice",
    genPDF:"Generate PDF Report", pdfDl:"Downloading PDF...",
    dragDrop:"Drag & drop or click to upload", supported:"JPG, PNG supported",
    vidSupport:"MP4, AVI, MOV supported", scores:"Confidence Scores",
    frameResults:"Frame-by-Frame Results", mostDetected:"Most Detected",
    avgDamage:"Average Damage", framesAnalyzed:"Frames Analyzed",
    complete:"Analysis Complete",
  },
  ur: {
    analyzing:"تصویر جانچی جا رہی ہے...", processing:"ویڈیو جانچی جا رہی ہے...",
    detecting:"جگہ تلاش ہو رہی ہے...", noFile:"پہلے فائل منتخب کریں۔",
    confidence:"یقین", disease:"بیماری", damage:"پتے کا نقصان",
    severity:"شدت", treatment:"علاج کی سفارشات",
    fungicide:"پھپھوندی کش / اسپرے", fertilizer:"کھاد",
    precautions:"احتیاطی تدابیر", weatherAdv:"موسم کے مطابق مشورہ",
    genPDF:"رپورٹ بنائیں", pdfDl:"رپورٹ ڈاؤنلوڈ ہو رہی ہے...",
    dragDrop:"یہاں فائل ڈراپ کریں یا کلک کریں", supported:"JPG، PNG قابل قبول",
    vidSupport:"MP4، AVI، MOV قابل قبول", scores:"یقین کے اعداد",
    frameResults:"فریم وار نتائج", mostDetected:"سب سے زیادہ",
    avgDamage:"اوسط نقصان", framesAnalyzed:"فریم جانچے",
    complete:"تجزیہ مکمل",
  }
};

let LANG = document.documentElement.getAttribute("data-lang") || "en";
const T = k => (TX[LANG]||TX.en)[k] || k;

function setLang(lang) {
  LANG = lang;
  document.documentElement.setAttribute("data-lang", lang);
  document.querySelectorAll(".lang-btn").forEach(b => b.classList.toggle("active", b.dataset.lang === lang));
  fetch("/set-lang",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({lang})});
  document.querySelectorAll("[data-t]").forEach(el => { const v=T(el.dataset.t); if(v) el.textContent=v; });
}

const showLoader = msg => {
  const el = document.getElementById("loader");
  if(el){ el.querySelector(".loader-text").textContent = msg||T("analyzing"); el.classList.add("show"); }
};
const hideLoader = () => document.getElementById("loader")?.classList.remove("show");

function initParticles() {
  const canvas = document.getElementById("particles");
  if(!canvas) return;
  const ctx = canvas.getContext("2d");
  const resize = () => { canvas.width = innerWidth; canvas.height = innerHeight; };
  resize(); window.addEventListener("resize", resize);
  const pts = Array.from({length:48}, () => ({
    x: Math.random()*innerWidth, y: Math.random()*innerHeight,
    r: Math.random()*2+.5, vy:-(Math.random()*.45+.12),
    vx:(Math.random()-.5)*.22, a:Math.random()*.38+.1
  }));
  const draw = () => {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    pts.forEach(p => {
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(74,222,128,${p.a})`; ctx.fill();
      p.y+=p.vy; p.x+=p.vx;
      if(p.y<-5){ p.y=canvas.height+5; p.x=Math.random()*canvas.width; }
    });
    requestAnimationFrame(draw);
  };
  draw();
}

function initTabs() {
  document.querySelectorAll(".tab-group").forEach(grp => {
    grp.querySelectorAll(".tab-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        grp.querySelectorAll(".tab-btn").forEach(b=>b.classList.remove("active"));
        grp.querySelectorAll(".tab-pane").forEach(p=>p.classList.remove("active"));
        btn.classList.add("active");
        grp.querySelector(`[data-tab="${btn.dataset.target}"]`)?.classList.add("active");
      });
    });
  });
}

function initUploadZones() {
  document.querySelectorAll(".upload-zone").forEach(zone => {
    zone.addEventListener("dragover", e=>{ e.preventDefault(); zone.classList.add("dragover"); });
    zone.addEventListener("dragleave", ()=>zone.classList.remove("dragover"));
    zone.addEventListener("drop", e=>{
      e.preventDefault(); zone.classList.remove("dragover");
      const inp = zone.querySelector("input[type='file']");
      if(inp && e.dataTransfer.files.length){
        inp.files = e.dataTransfer.files;
        inp.dispatchEvent(new Event("change",{bubbles:true}));
      }
    });
  });
}

function initImagePreview() {
  const inp = document.getElementById("imgInput");
  const box = document.getElementById("imgPreviewBox");
  const img = document.getElementById("imgPreviewEl");
  if(!inp||!box) return;
  inp.addEventListener("change", () => {
    if(!inp.files[0]) return;
    const reader = new FileReader();
    reader.onload = e=>{ img.src=e.target.result; box.style.display="block"; };
    reader.readAsDataURL(inp.files[0]);
  });
}

const sevTag  = s => ({Mild:"tag-green",Moderate:"tag-yellow",Severe:"tag-red"}[s]||"tag-gray");
const riskTag = l => ({low:"tag-green",medium:"tag-orange",high:"tag-red"}[l]||"tag-gray");

function renderResult(data, containerId="resultSection") {
  const sec = document.getElementById(containerId);
  if(!sec) return;
  sec.style.display = "block";
  sec.scrollIntoView({behavior:"smooth", block:"start"});

  const boxCls = data.disease==="healthy" ? "glass g-success result-header" : "glass g-danger result-header";
  const riskLv = data.weather?.overall_level||"low";

  let scoresHtml = "";
  if(data.all_scores_labels && Object.keys(data.all_scores_labels).length){
    const entries = Object.entries(data.all_scores_labels);
    scoresHtml = `
    <div class="glass" style="padding:18px 22px;margin-bottom:14px">
      <div style="font-size:10px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:12px">${T("scores")}</div>
      ${entries.map(([lbl,val])=>`
        <div style="margin-bottom:9px">
          <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
            <span style="color:rgba(255,255,255,.8)">${lbl}</span>
            <span style="color:var(--accent);font-weight:800">${val}%</span>
          </div>
          <div class="prog-wrap">
            <div class="prog-fill" style="width:${val}%;background:${lbl===data.disease_name?'linear-gradient(90deg,#4ade80,#86efac)':'rgba(255,255,255,0.18)'}"></div>
          </div>
        </div>`).join("")}
    </div>`;
  }

  sec.innerHTML = `
    <div class="${boxCls}" style="animation:fadeUp .4s ease both">
      <h3>${data.disease_name}</h3>
      <p>${data.description}</p>
      <div style="margin-top:9px">
        <span class="tag ${sevTag(data.severity)}">${data.severity}</span>
        <span class="tag ${riskTag(riskLv)}">Risk: ${riskLv}</span>
      </div>
    </div>

    <div class="metrics-grid">
      <div class="glass metric-card"><div class="metric-label">${T("disease")}</div><div class="metric-value" style="font-size:1rem">${data.disease_name}</div></div>
      <div class="glass metric-card"><div class="metric-label">${T("confidence")}</div><div class="metric-value">${data.confidence}%</div></div>
      <div class="glass metric-card"><div class="metric-label">${T("damage")}</div><div class="metric-value">${data.damage_pct}%</div></div>
      <div class="glass metric-card"><div class="metric-label">${T("severity")}</div><div class="metric-value" style="font-size:1rem">${data.severity}</div></div>
    </div>

    ${scoresHtml}

    <div style="margin-bottom:14px">
      <div style="font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:10px;padding-left:2px">${T("treatment")}</div>
      <div class="treatment-grid">
        <div class="glass treatment-col">
          <div class="treatment-col-title">${T("fungicide")}</div>
          ${data.fungicide.map(i=>`<div class="treatment-item">${i}</div>`).join("")}
        </div>
        <div class="glass treatment-col">
          <div class="treatment-col-title">${T("fertilizer")}</div>
          ${data.fertilizer.map(i=>`<div class="treatment-item">${i}</div>`).join("")}
        </div>
        <div class="glass treatment-col">
          <div class="treatment-col-title">${T("precautions")}</div>
          ${data.precautions.map(i=>`<div class="treatment-item">${i}</div>`).join("")}
        </div>
      </div>
    </div>

    <div class="glass ${riskLv==='high'?'g-danger':riskLv==='medium'?'g-warn':'g-success'}" style="padding:16px 20px;margin-bottom:14px">
      <div style="font-size:10px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:5px">${T("weatherAdv")}</div>
      <div style="font-size:14px;font-weight:800;margin-bottom:5px">${data.weather?.overall_label||""}</div>
      <div style="color:var(--muted);font-size:13px">${data.weather_advice}</div>
    </div>

    <div style="display:flex;gap:10px;flex-wrap:wrap">
      <button class="btn btn-primary" onclick="dlPDF(${data.scan_id})">📄 ${T("genPDF")}</button>
    </div>
  `;
}

function dlPDF(id){
  showLoader(T("pdfDl"));
  window.location.href=`/generate-pdf/${id}`;
  setTimeout(hideLoader,2500);
}

function showErr(msg, containerId="resultSection"){
  const s=document.getElementById(containerId);
  if(s){ s.style.display="block"; s.innerHTML=`<div class="glass g-danger" style="padding:16px 20px"><strong>Error:</strong> ${msg}</div>`; }
}

function initDetectForm() {
  const form = document.getElementById("detectForm");
  if(!form) return;
  form.addEventListener("submit", async e=>{
    e.preventDefault();
    const inp = document.getElementById("imgInput");
    if(!inp?.files?.length){ alert(T("noFile")); return; }
    showLoader(T("analyzing"));
    const fd = new FormData(form);
    fd.set("lang", LANG);
    fd.set("city", document.getElementById("cityInput")?.value||"Rahim Yar Khan");
    try{
      const res  = await fetch("/detect",{method:"POST",body:fd});
      const data = await res.json();
      hideLoader();
      if(data.error){ showErr(data.error); return; }
      renderResult(data);
    }catch(err){ hideLoader(); showErr(err.message); }
  });
}

function initVideoForm() {
  const form = document.getElementById("videoForm");
  if(!form) return;

  document.getElementById("videoInput")?.addEventListener("change", function(){
    const wrap = document.getElementById("videoPreviewWrap");
    const vid  = document.getElementById("videoPreview");
    if(this.files[0] && wrap && vid){
      vid.src=URL.createObjectURL(this.files[0]);
      wrap.style.display="block";
    }
  });

  form.addEventListener("submit", async e=>{
    e.preventDefault();
    const inp = document.getElementById("videoInput");
    if(!inp?.files?.length){ alert(T("noFile")); return; }
    showLoader(T("processing"));
    const fd = new FormData(form);
    fd.set("lang", LANG);
    try{
      const res  = await fetch("/detect-video",{method:"POST",body:fd});
      const data = await res.json();
      hideLoader();
      if(data.error){ showErr(data.error,"videoResult"); return; }
      renderVideoResult(data);
    }catch(err){ hideLoader(); showErr(err.message,"videoResult"); }
  });
}

function renderVideoResult(data){
  const sec = document.getElementById("videoResult");
  if(!sec) return;
  sec.style.display="block";
  sec.scrollIntoView({behavior:"smooth",block:"start"});
  sec.innerHTML=`
    <div class="metrics-grid" style="margin-bottom:14px">
      <div class="glass metric-card"><div class="metric-label">${T("mostDetected")}</div><div class="metric-value" style="font-size:.9rem">${data.top_disease}</div></div>
      <div class="glass metric-card"><div class="metric-label">${T("avgDamage")}</div><div class="metric-value">${data.avg_damage}%</div></div>
      <div class="glass metric-card"><div class="metric-label">${T("framesAnalyzed")}</div><div class="metric-value">${data.frame_count}</div></div>
      <div class="glass metric-card"><div class="metric-label">Status</div><div class="metric-value" style="font-size:.85rem;color:var(--accent)">${T("complete")}</div></div>
    </div>
    <div style="font-size:11px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:10px">${T("frameResults")}</div>
    ${data.results.map(r=>`
      <div class="glass history-row" style="margin:4px 0">
        <div class="history-info">
          <div class="history-title">Frame ${r.frame} — ${r.disease_name}</div>
          <div class="history-meta">Confidence: ${r.conf}% &nbsp;·&nbsp; Damage: ${r.damage}%</div>
        </div>
        <span class="tag ${sevTag(r.severity)}">${r.severity}</span>
      </div>`).join("")}
  `;
}

function initWebcam(){
  document.getElementById("webcamInput")?.addEventListener("change", function(){
    if(!this.files[0]) return;
    const img  = document.getElementById("webcamPreviewImg");
    const wrap = document.getElementById("webcamPreviewWrap");
    if(img) img.src=URL.createObjectURL(this.files[0]);
    if(wrap) wrap.style.display="block";
  });
}

async function analyzeWebcam(){
  const inp = document.getElementById("webcamInput");
  if(!inp?.files?.[0]) return;
  showLoader(T("analyzing"));
  const fd = new FormData();
  fd.append("image", inp.files[0]);
  fd.append("lang", LANG);
  fd.append("city", document.getElementById("cityInput")?.value||"Rahim Yar Khan");
  try{
    const res  = await fetch("/detect",{method:"POST",body:fd});
    const data = await res.json();
    hideLoader();
    if(data.error){ showErr(data.error); return; }
    renderResult(data);
    document.getElementById("resultSection").style.display="block";
    document.getElementById("resultSection").scrollIntoView({behavior:"smooth"});
  }catch(e){ hideLoader(); showErr(e.message); }
}

async function detectLocation(){
  const btn = document.getElementById("detectLocBtn");
  const dis = document.getElementById("locDisplay");
  if(btn) btn.disabled=true;
  if(dis) dis.textContent=T("detecting");
  try{
    const res  = await fetch("/detect-location");
    const data = await res.json();
    if(data.success){
      if(dis) dis.textContent=`📍 ${data.display}`;
      const ci = document.getElementById("cityInput");
      if(ci) ci.value=data.city;
      await fetch("/set-city",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({city:data.city})
      });
    } else {
      if(dis) dis.textContent="Could not detect — enter manually";
    }
  }catch{ if(dis) dis.textContent="Detection failed"; }
  if(btn) btn.disabled=false;
}

function initCityInput(){
  const inp = document.getElementById("cityInput");
  if(!inp) return;
  let timer;
  inp.addEventListener("input", ()=>{
    clearTimeout(timer);
    timer=setTimeout(()=>{
      fetch("/set-city",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({city:inp.value})
      });
    }, 600);
  });
  const h = document.getElementById("cityHidden");
  if(h) inp.addEventListener("input", ()=>{ h.value=inp.value; });
}

document.addEventListener("DOMContentLoaded", ()=>{
  initParticles();
  initTabs();
  initUploadZones();
  initImagePreview();
  initDetectForm();
  initVideoForm();
  initWebcam();
  initCityInput();

  document.querySelectorAll(".lang-btn").forEach(b=>{
    b.addEventListener("click", ()=>setLang(b.dataset.lang));
  });

  const obs = new IntersectionObserver(entries=>{
    entries.forEach(e=>{
      if(e.isIntersecting) e.target.style.animation="fadeUp .4s ease both";
    });
  },{threshold:.08});
  document.querySelectorAll(".glass,.metric-card").forEach(el=>obs.observe(el));
});