// DOA Nutrition — umumiy JS

function toggleSidebar() {
  // Mobil (<=860px): sidebar ustidan ochiladi (overlay)
  if (window.matchMedia('(max-width: 860px)').matches) {
    var s = document.getElementById('sidebar');
    var b = document.getElementById('backdrop');
    if (s) s.classList.toggle('open');
    if (b) b.classList.toggle('show');
    return;
  }
  // Kompyuter: sidebar ichkariga kirib/chiqib yopiladi-ochiladi
  var el = document.documentElement;
  var collapsed = el.getAttribute('data-nav') === 'collapsed';
  if (collapsed) el.removeAttribute('data-nav');
  else el.setAttribute('data-nav', 'collapsed');
  try { localStorage.setItem('doa-nav', collapsed ? '' : 'collapsed'); } catch (e) {}
}

// Sayt yaqinlashib (zoom) ketmasligi uchun: pinch / ctrl+scroll / klaviatura zoom'ni to'xtatish
document.addEventListener('wheel', function (e) {
  if (e.ctrlKey) e.preventDefault();
}, { passive: false });
document.addEventListener('keydown', function (e) {
  if ((e.ctrlKey || e.metaKey) && ['+', '-', '=', '_', '0'].indexOf(e.key) !== -1) {
    e.preventDefault();
  }
});

// Dropdown (til / shrift / akkount)
function toggleDrop(id, ev) {
  var d = document.getElementById(id);
  if (!d) return;
  var open = d.classList.contains('open');
  document.querySelectorAll('.dropdown.open').forEach(function (x) { x.classList.remove('open'); });
  if (!open) d.classList.add('open');
  if (ev) ev.stopPropagation();
}
document.addEventListener('click', function (e) {
  // Menyu ichida bosilsa yopmaymiz (til formasi/shrift tugmalari ishlashi uchun)
  if (e.target.closest('.dd-menu')) return;
  document.querySelectorAll('.dropdown.open').forEach(function (x) { x.classList.remove('open'); });
});

// O'chirishni tasdiqlash modali (browser confirm o'rniga)
function confirmDelete(btn) {
  var url = btn.getAttribute('data-del');
  var m = document.getElementById('confirmModal');
  var form = document.getElementById('confirmForm');
  if (!m || !form) return;
  form.setAttribute('action', url);
  m.classList.add('open');
}
function closeConfirm() {
  var m = document.getElementById('confirmModal');
  if (m) m.classList.remove('open');
}
document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeConfirm(); });

// Tema (dark / light)
function toggleTheme() {
  var el = document.documentElement;
  var next = el.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
  el.setAttribute('data-theme', next);
  try { localStorage.setItem('doa-theme', next); } catch (e) {}
}

// Shrift o'lchami: '' (oddiy), 's', 'l', 'xl'
function setFont(v) {
  var el = document.documentElement;
  if (v) el.setAttribute('data-fs', v); else el.removeAttribute('data-fs');
  try { localStorage.setItem('doa-fs', v || ''); } catch (e) {}
  syncFontUI();
}

// Qalin (bold) rejim
function toggleBold() {
  var el = document.documentElement;
  var on = el.getAttribute('data-fw') === 'bold';
  if (on) el.removeAttribute('data-fw'); else el.setAttribute('data-fw', 'bold');
  try { localStorage.setItem('doa-fw', on ? '' : 'bold'); } catch (e) {}
  syncFontUI();
}

function syncFontUI() {
  var fs = document.documentElement.getAttribute('data-fs') || '';
  document.querySelectorAll('.fs-opt').forEach(function (b) {
    b.classList.toggle('active', (b.getAttribute('data-v') || '') === fs);
  });
  var bold = document.documentElement.getAttribute('data-fw') === 'bold';
  document.querySelectorAll('.fw-opt').forEach(function (b) { b.classList.toggle('active', bold); });
}
document.addEventListener('DOMContentLoaded', syncFontUI);

// Sonlarni animatsiya bilan "o'sish" ($ formatida)
function fmtPul(v) {
  return '$' + Number(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function countUp(el) {
  var target = parseFloat(el.getAttribute('data-count')) || 0;
  if (!target) return;
  var dur = 850, start = null;
  function step(now) {
    if (start === null) start = now;
    var p = Math.min((now - start) / dur, 1);
    var ease = 1 - Math.pow(1 - p, 3);
    el.textContent = fmtPul(target * ease);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
document.addEventListener('DOMContentLoaded', function () {
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.querySelectorAll('[data-count]').forEach(countUp);
});

// ============================================================
//  Excel'simon ustun filtrlari + saralash (barcha .ftable jadvallar)
// ============================================================
(function () {
  var FUNNEL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>';
  var pop = null, cur = null; // cur = {table, col, btn}

  function t(s) { return document.documentElement.lang === 'ru' ? s.ru : (document.documentElement.lang === 'en' ? s.en : (document.documentElement.lang === 'tr' ? s.tr : s.uz)); }
  var L = {
    az:   { uz: 'O‘sish bo‘yicha', ru: 'По возрастанию', en: 'Sort A→Z', tr: 'Artan' },
    za:   { uz: 'Kamayish bo‘yicha', ru: 'По убыванию', en: 'Sort Z→A', tr: 'Azalan' },
    find: { uz: 'Qidirish…', ru: 'Поиск…', en: 'Search…', tr: 'Ara…' },
    all:  { uz: '(Barchasi)', ru: '(Все)', en: '(All)', tr: '(Tümü)' },
    clr:  { uz: 'Tozalash', ru: 'Сбросить', en: 'Clear', tr: 'Temizle' },
    ok:   { uz: 'Qo‘llash', ru: 'Применить', en: 'Apply', tr: 'Uygula' }
  };

  function dataRows(table) {
    var out = [];
    if (!table.tBodies.length) return out;
    Array.prototype.forEach.call(table.tBodies[0].rows, function (r) {
      if (!r.querySelector('td.empty')) out.push(r);
    });
    return out;
  }
  function cellText(tr, col) {
    var c = tr.children[col];
    return c ? c.textContent.trim().replace(/\s+/g, ' ') : '';
  }
  function numVal(s) {
    var n = parseFloat(String(s).replace(/[^0-9.\-]/g, ''));
    return isNaN(n) ? null : n;
  }
  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function applyFilters(table) {
    var f = table._filters || {};
    dataRows(table).forEach(function (tr) {
      var show = true;
      for (var col in f) {
        if (!f[col].has(cellText(tr, +col))) { show = false; break; }
      }
      tr.style.display = show ? '' : 'none';
    });
  }
  function sortBy(table, col, dir) {
    var rows = dataRows(table);
    rows.sort(function (a, b) {
      var x = cellText(a, col), y = cellText(b, col);
      var nx = numVal(x), ny = numVal(y), r;
      if (nx !== null && ny !== null) r = nx - ny;
      else r = x.localeCompare(y, undefined, { numeric: true });
      return dir === 'za' ? -r : r;
    });
    var tb = table.tBodies[0];
    rows.forEach(function (r) { tb.appendChild(r); });
  }

  function closePop() {
    if (pop) pop.classList.remove('open');
    cur = null;
  }
  function buildPop() {
    pop = document.createElement('div');
    pop.className = 'fpop';
    document.body.appendChild(pop);
  }
  function openPop(table, col, btn) {
    if (!pop) buildPop();
    cur = { table: table, col: col, btn: btn };
    var active = (table._filters && table._filters[col]) || null;
    // mavjud qiymatlar (ko'rinadigan boshqa filtrlar hisobga olinmaydi — oddiylik uchun barchasi)
    var vals = {};
    dataRows(table).forEach(function (tr) { vals[cellText(tr, col)] = true; });
    var list = Object.keys(vals).sort(function (a, b) {
      var na = numVal(a), nb = numVal(b);
      if (na !== null && nb !== null) return na - nb;
      return a.localeCompare(b, undefined, { numeric: true });
    });
    var html = '';
    html += '<div class="fsort">';
    html += '<button type="button" data-sort="az"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 20V4M6 4l-3 3M6 4l3 3"/><path d="M13 6h7M13 12h5M13 18h3"/></svg>' + t(L.az) + '</button>';
    html += '<button type="button" data-sort="za"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4v16M6 20l-3-3M6 20l3-3"/><path d="M13 6h3M13 12h5M13 18h7"/></svg>' + t(L.za) + '</button>';
    html += '</div>';
    html += '<input type="text" class="fsearch" placeholder="' + t(L.find) + '">';
    html += '<div class="flist">';
    html += '<label class="fitem all"><input type="checkbox" class="fall" checked><span>' + t(L.all) + '</span></label>';
    list.forEach(function (v) {
      var ck = (!active || active.has(v)) ? 'checked' : '';
      var disp = esc(v === '' ? '—' : v);
      // XSS himoyasi: foydalanuvchi kiritgan matn HTML sifatida emas, matn sifatida chiqadi
      html += '<label class="fitem"><input type="checkbox" class="fck" value="' + esc(v) + '" ' + ck + '><span title="' + disp + '">' + disp + '</span></label>';
    });
    html += '</div>';
    html += '<div class="facts"><button type="button" class="fclear">' + t(L.clr) + '</button><button type="button" class="fapply">' + t(L.ok) + '</button></div>';
    pop.innerHTML = html;
    pop.classList.add('open');
    syncAll();
    // joylashuv
    var r = btn.getBoundingClientRect();
    var w = pop.offsetWidth, h = pop.offsetHeight;
    var left = Math.min(r.left, window.innerWidth - w - 12);
    var top = r.bottom + 6;
    if (top + h > window.innerHeight - 8) top = Math.max(8, r.top - h - 6);
    pop.style.left = Math.max(8, left) + 'px';
    pop.style.top = top + 'px';

    var search = pop.querySelector('.fsearch');
    search.addEventListener('input', function () {
      var q = search.value.toLowerCase();
      pop.querySelectorAll('.flist .fitem:not(.all)').forEach(function (it) {
        var txt = it.querySelector('span').textContent.toLowerCase();
        it.style.display = txt.indexOf(q) > -1 ? '' : 'none';
      });
    });
    pop.querySelector('.fall').addEventListener('change', function () {
      var on = this.checked;
      pop.querySelectorAll('.fck').forEach(function (c) {
        if (c.closest('.fitem').style.display !== 'none') c.checked = on;
      });
    });
    pop.querySelectorAll('.fck').forEach(function (c) { c.addEventListener('change', syncAll); });
    pop.querySelectorAll('[data-sort]').forEach(function (b) {
      b.addEventListener('click', function () { sortBy(table, col, b.getAttribute('data-sort')); closePop(); });
    });
    pop.querySelector('.fclear').addEventListener('click', function () {
      if (table._filters) delete table._filters[col];
      applyFilters(table); btn.classList.remove('on'); closePop();
    });
    pop.querySelector('.fapply').addEventListener('click', function () {
      var checked = [], total = 0;
      pop.querySelectorAll('.fck').forEach(function (c) { total++; if (c.checked) checked.push(c.value); });
      table._filters = table._filters || {};
      if (checked.length === total) { delete table._filters[col]; btn.classList.remove('on'); }
      else { table._filters[col] = new Set(checked); btn.classList.add('on'); }
      applyFilters(table); closePop();
    });
    search.focus();
  }
  function syncAll() {
    if (!pop) return;
    var all = pop.querySelector('.fall'); if (!all) return;
    var cks = pop.querySelectorAll('.fck'), on = 0;
    cks.forEach(function (c) { if (c.checked) on++; });
    all.checked = on === cks.length;
    all.indeterminate = on > 0 && on < cks.length;
  }

  function initTable(table) {
    var ths = table.tHead ? table.tHead.rows[0].cells : [];
    Array.prototype.forEach.call(ths, function (th, i) {
      if (th.classList.contains('nofilter') || !th.textContent.trim()) return;
      th.classList.add('th-f');
      var label = document.createElement('span');
      label.className = 'th-label';
      while (th.firstChild) label.appendChild(th.firstChild);
      th.appendChild(label);
      var btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'fbtn'; btn.innerHTML = FUNNEL;
      btn.setAttribute('aria-label', 'filter');
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (cur && cur.table === table && cur.col === i && pop.classList.contains('open')) { closePop(); return; }
        openPop(table, i, btn);
      });
      th.appendChild(btn);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('table.ftable').forEach(initTable);
  });
  document.addEventListener('click', function (e) {
    if (pop && pop.classList.contains('open') && !pop.contains(e.target) && !e.target.closest('.fbtn')) closePop();
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePop(); });
  window.addEventListener('resize', closePop);
})();

// ============================================================
//  Saqlanmoqda / yuklanmoqda overlay (form yuborilganda)
// ============================================================
(function () {
  var overlay = null;
  function ensure() {
    if (overlay) return overlay;
    overlay = document.createElement('div');
    overlay.className = 'saving-overlay';
    overlay.innerHTML = '<div class="sv-box"><div class="sv-spin"></div>' +
      '<div class="sv-text"><span class="sv-label"></span><span class="sv-dots"></span></div></div>';
    document.body.appendChild(overlay);
    return overlay;
  }
  function show(text) {
    var o = ensure();
    o.querySelector('.sv-label').textContent = text || 'Saqlanmoqda';
    // reflow -> transition
    o.offsetWidth;
    o.classList.add('show');
  }
  function hide() { if (overlay) overlay.classList.remove('show'); }

  function bind() {
    document.querySelectorAll('form[data-loading]').forEach(function (form) {
      if (form.__svBound) return;
      form.__svBound = true;
      form.addEventListener('submit', function (e) {
        if (form.__saving) return;
        if ((form.getAttribute('method') || 'get').toLowerCase() !== 'post') return;
        e.preventDefault();
        form.__saving = true;
        show(form.getAttribute('data-loading') || 'Saqlanmoqda');
        // qisqa kechikish — "saqlanmoqda" ko'rinib tursin, keyin jo'natadi
        setTimeout(function () { form.submit(); }, 850);
      });
    });
  }
  document.addEventListener('DOMContentLoaded', bind);
  // Orqaga/bfcache qaytganda overlay yopiq bo'lsin
  window.addEventListener('pageshow', function (e) { if (e.persisted) hide(); });
})();

// ============================================================
//  Excel (.xlsx) eksport — filter bo'yicha yoki hammasi
// ============================================================
function exportXlsx(mode) {
  var table = document.querySelector('table.ftable');
  var filters = {};
  if (mode === 'filter' && table && table._filters) {
    for (var k in table._filters) { filters[k] = Array.from(table._filters[k]); }
  }
  var tok = document.querySelector('[name=csrfmiddlewaretoken]');
  tok = tok ? tok.value : '';
  var drop = document.getElementById('expDrop');
  if (drop) drop.classList.remove('open');
  var nom = (document.title.split(' ·')[0] || 'hisobot').trim();
  fetch(window.location.pathname, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': tok },
    body: JSON.stringify({ mode: mode, filters: filters })
  }).then(function (r) {
    if (!r.ok) throw new Error(r.status);
    return r.blob();
  }).then(function (b) {
    var url = URL.createObjectURL(b);
    var a = document.createElement('a');
    a.href = url; a.download = 'DOA-' + nom + '.xlsx';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1500);
  }).catch(function (e) { console.error('Eksport xatosi:', e); });
}

// ============================================================
//  Sidebar guruhlari — yig'iladigan (dropdown), holati eslab qolinadi
// ============================================================
function toggleNav(btn) {
  var g = btn.closest('.nav-group');
  if (!g) return;
  g.classList.toggle('open');
  try {
    var closed = JSON.parse(localStorage.getItem('doa-nav-closed') || '[]');
    var k = g.getAttribute('data-g');
    var i = closed.indexOf(k);
    if (g.classList.contains('open')) { if (i > -1) closed.splice(i, 1); }
    else if (i < 0) { closed.push(k); }
    localStorage.setItem('doa-nav-closed', JSON.stringify(closed));
  } catch (e) {}
}
document.addEventListener('DOMContentLoaded', function () {
  var closed = [];
  try { closed = JSON.parse(localStorage.getItem('doa-nav-closed') || '[]'); } catch (e) {}
  document.querySelectorAll('.nav-group').forEach(function (g) {
    // Faol sahifa joylashgan guruh doim ochiq turadi
    if (g.querySelector('.nav-item.active')) { g.classList.add('open'); return; }
    if (closed.indexOf(g.getAttribute('data-g')) > -1) { g.classList.remove('open'); }
  });
});

// ============================================================
//  Toast bildirishnomalar — browser alert o'rniga chiroyli oyna
// ============================================================
function closeToast(el) {
  var t = (el && el.classList && el.classList.contains('toast')) ? el : (el ? el.closest('.toast') : null);
  if (!t) return;
  t.classList.remove('show');
  t.classList.add('hide');
  setTimeout(function () { t.remove(); }, 450);
}
function _toastActivate(t) {
  requestAnimationFrame(function () { t.offsetWidth; t.classList.add('show'); });
  var ms = t.classList.contains('toast-error') ? 7000 : 4500;
  var timer = setTimeout(function () { closeToast(t); }, ms);
  t.addEventListener('mouseenter', function () { clearTimeout(timer); });
}
function showToast(msg, type) {
  var wrap = document.getElementById('toastWrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.className = 'toast-wrap'; wrap.id = 'toastWrap';
    var c = document.querySelector('.content') || document.body;
    c.appendChild(wrap);
  }
  var ICO = {
    success: '<polyline points="20 6 9 17 4 12"/>',
    error: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    warning: '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>'
  };
  type = type || 'info';
  var ico = ICO[type] || ICO.warning;
  var t = document.createElement('div');
  t.className = 'toast toast-' + type;
  t.innerHTML = '<span class="toast-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">' + ico + '</svg></span>' +
    '<span class="toast-msg"></span>' +
    '<button type="button" class="toast-x" onclick="closeToast(this)"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>';
  t.querySelector('.toast-msg').textContent = msg;
  wrap.appendChild(t);
  _toastActivate(t);
}
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('#toastWrap .toast').forEach(_toastActivate);
});
