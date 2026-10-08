/* Administration : modales (ajouter / voir / modifier / supprimer), colonne d'actions et déconnexion élégante. */
(function () {
  const inFrame = window.self !== window.top || location.search.includes("_popup=1");
  if (inFrame) return;

  const css = `
  .am-ov{position:fixed;inset:0;background:rgba(15,23,42,.55);z-index:9999;display:none;align-items:center;justify-content:center;padding:16px}
  .am-ov.open{display:flex;animation:am-fade .15s ease-out}
  @keyframes am-fade{from{opacity:0}to{opacity:1}}
  .am-box{background:#fff;color:#1f2937;width:min(760px,100%);height:min(86vh,720px);border-radius:14px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.35)}
  .am-box.sm{height:min(86vh,470px);width:min(560px,100%)}
  html.dark .am-box{background:#111827;color:#f3f4f6}
  .am-hd{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid rgba(128,128,128,.25);font-weight:600}
  .am-x{background:none;border:0;font-size:24px;line-height:1;cursor:pointer;color:inherit;padding:2px 8px;border-radius:6px}
  .am-x:hover{background:rgba(128,128,128,.2)}
  .am-fr{flex:1;border:0;width:100%;background:transparent}
  .am-btn{display:inline-flex;align-items:center;padding:5px;margin-left:2px;border-radius:8px;color:#6b7280;text-decoration:none}
  .am-btn:hover{background:rgba(128,128,128,.18)}
  .am-btn .material-symbols-outlined{font-size:20px}
  .am-edit{color:#0f766e}.am-del{color:#dc2626}.am-del:hover{background:rgba(220,38,38,.12)}
  html.dark .am-edit{color:#2dd4bf}
  a[href$="#logout"]{color:#dc2626!important;margin-top:4px}
  a[href$="#logout"]:hover{background:rgba(220,38,38,.1)!important}
  .am-lo{width:min(420px,100%);padding:30px 26px;text-align:center;border-radius:16px}
  .am-lo .ic{width:56px;height:56px;border-radius:50%;background:rgba(220,38,38,.12);color:#dc2626;display:grid;place-items:center;margin:0 auto 14px}
  .am-lo .ic span{font-size:30px}
  .am-lo h3{margin:0 0 6px;font-size:20px}.am-lo p{margin:0 0 22px;opacity:.7}
  .am-lo .bt{display:flex;gap:10px;justify-content:center}
  .am-lo button{font:600 15px system-ui,sans-serif;border-radius:8px;padding:10px 20px;cursor:pointer;border:1px solid rgba(128,128,128,.4);background:transparent;color:inherit}
  .am-lo button.go{background:#dc2626;border-color:#dc2626;color:#fff}.am-lo button.go:hover{background:#b91c1c}`;
  const st = document.createElement("style");
  st.textContent = css;
  document.head.appendChild(st);

  /* ---------- Modale à iframe ---------- */
  const ov = document.createElement("div");
  ov.className = "am-ov";
  ov.innerHTML = '<div class="am-box" role="dialog" aria-modal="true"><div class="am-hd"><span id="am-t"></span>' +
    '<button class="am-x" type="button" aria-label="Fermer">&times;</button></div><iframe class="am-fr" title="Formulaire"></iframe></div>';
  document.body.appendChild(ov);
  const box = ov.querySelector(".am-box"), fr = ov.querySelector("iframe"), title = ov.querySelector("#am-t");

  const close = () => { ov.classList.remove("open"); fr.src = "about:blank"; };
  const open = (url, label, small) => {
    const u = new URL(url, location.origin);
    u.searchParams.set("_popup", "1");
    title.textContent = label;
    box.classList.toggle("sm", !!small);
    fr.src = u.toString();
    ov.classList.add("open");
  };
  ov.querySelector(".am-x").onclick = close;
  ov.addEventListener("mousedown", e => { if (e.target === ov) close(); });
  document.addEventListener("keydown", e => {
    if (e.key !== "Escape") return;
    if (ov.classList.contains("open")) close();
    if (lo.classList.contains("open")) lo.classList.remove("open");
  });
  window.addEventListener("message", e => {
    if (e.origin === location.origin && e.data && e.data.type === "admin-modal-saved") { close(); location.reload(); }
  });

  /* ---------- Confirmation de déconnexion ---------- */
  const lo = document.createElement("div");
  lo.className = "am-ov";
  lo.innerHTML = '<div class="am-box am-lo" role="alertdialog" aria-modal="true"><div class="ic"><span class="material-symbols-outlined">logout</span></div>' +
    '<h3>Se déconnecter ?</h3><p>Vous allez quitter l\'administration. Vous pourrez vous reconnecter à tout moment.</p>' +
    '<div class="bt"><button type="button" class="no">Rester connecté</button><button type="button" class="go">Se déconnecter</button></div></div>';
  document.body.appendChild(lo);
  lo.querySelector(".no").onclick = () => lo.classList.remove("open");
  lo.addEventListener("mousedown", e => { if (e.target === lo) lo.classList.remove("open"); });
  lo.querySelector(".go").onclick = () => {
    const f = document.createElement("form");
    f.method = "post"; f.action = "/admin/logout/";
    const t = (document.cookie.match(/csrftoken=([^;]+)/) || [])[1] || (document.querySelector("[name=csrfmiddlewaretoken]") || {}).value || "";
    f.innerHTML = '<input type="hidden" name="csrfmiddlewaretoken" value="' + t + '">';
    document.body.appendChild(f);
    f.submit();
  };

  /* ---------- Colonne d'actions (Voir / Modifier / Supprimer) ---------- */
  function addActions() {
    const t = document.querySelector("#result_list");
    const head = t && t.querySelector("thead tr");
    if (!head || head.querySelector(".am-act")) return;
    const rows = [...t.querySelectorAll("tbody tr")].map(tr => ({ tr, a: tr.querySelector('a[href*="/change/"]') })).filter(x => x.a);
    if (!rows.length) return;
    const th = document.createElement("th");
    th.className = head.lastElementChild.className + " am-act";
    th.style.textAlign = "right";
    th.textContent = "Actions";
    head.appendChild(th);
    rows.forEach(({ tr, a }) => {
      const base = new URL(a.href, location.origin).pathname.replace(/change\/$/, "");
      const td = document.createElement("td");
      td.className = tr.lastElementChild.className;
      td.style.cssText = "text-align:right;white-space:nowrap";
      const b = (href, cls, icon, label) => '<a class="am-btn ' + cls + '" href="' + href + '" title="' + label + '" aria-label="' + label + '"><span class="material-symbols-outlined">' + icon + '</span></a>';
      td.innerHTML = b(base + "change/?_view=1", "am-view", "visibility", "Voir") + b(base + "change/", "am-edit", "edit", "Modifier") + b(base + "delete/", "am-del", "delete", "Supprimer");
      tr.appendChild(td);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", addActions); else addActions();

  /* ---------- Interception des clics ---------- */
  document.addEventListener("click", e => {
    if (e.defaultPrevented || e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey) return;
    const a = e.target.closest("a[href]");
    if (!a) return;
    if (a.getAttribute("href").endsWith("#logout")) { e.preventDefault(); lo.classList.add("open"); return; }
    if (a.target === "_blank") return;
    const u = new URL(a.href, location.origin), path = u.pathname;
    if (!/^\/admin\/[^/]+\/[^/]+\//.test(path)) return;
    const inList = !!a.closest("#result_list");
    if (/\/add\/$/.test(path)) { e.preventDefault(); return open(a.href, "Ajouter"); }
    if (inList && /\/[^/]+\/change\/$/.test(path)) {
      e.preventDefault();
      return u.searchParams.has("_view") ? open(a.href, "Détails") : open(a.href, "Modifier");
    }
    if (inList && /\/[^/]+\/delete\/$/.test(path)) { e.preventDefault(); return open(a.href, "Supprimer", true); }
  }, true);
})();
