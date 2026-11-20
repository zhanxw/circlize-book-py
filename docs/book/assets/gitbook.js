(function () {
  "use strict";

  var bookEl = document.querySelector(".book");
  var toggleBtn = document.getElementById("sidebar-toggle");
  var searchInput = document.getElementById("book-search-input");
  var searchToggleBtn = document.getElementById("search-toggle-btn");
  var searchResultsEl = document.getElementById("search-results");
  var fontBtn = document.getElementById("font-settings-btn");
  var fontMenu = document.getElementById("font-settings-menu");
  var searchIndex = null;

  var savedTheme = localStorage.getItem("circlizepy_theme") || "white";
  var savedFont = localStorage.getItem("circlizepy_font") || "sans";
  var savedSize = parseInt(localStorage.getItem("circlizepy_size") || "16", 10);
  var savedSidebar = localStorage.getItem("circlizepy_sidebar");

  function applyTheme(theme) {
    document.body.classList.remove("theme-white", "theme-sepia", "theme-night");
    document.body.classList.add("theme-" + theme);
    localStorage.setItem("circlizepy_theme", theme);
    document.querySelectorAll("[data-theme]").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-theme") === theme);
    });
  }

  function applyFont(font) {
    document.body.classList.toggle("font-serif", font === "serif");
    localStorage.setItem("circlizepy_font", font);
    document.querySelectorAll("[data-font]").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-font") === font);
    });
  }

  function applySize(sz) {
    var clamped = Math.max(13, Math.min(22, sz));
    document.documentElement.style.setProperty("--font-size-base", clamped + "px");
    localStorage.setItem("circlizepy_size", String(clamped));
  }

  applyTheme(savedTheme);
  applyFont(savedFont);
  applySize(savedSize);

  if (savedSidebar === "closed" && window.innerWidth > 960 && bookEl) {
    bookEl.classList.add("without-summary");
  }

  if (toggleBtn && bookEl) {
    toggleBtn.addEventListener("click", function () {
      if (window.innerWidth <= 960) {
        bookEl.classList.toggle("mobile-summary-open");
      } else {
        bookEl.classList.toggle("without-summary");
        localStorage.setItem("circlizepy_sidebar", bookEl.classList.contains("without-summary") ? "closed" : "open");
      }
    });
  }

  if (fontBtn && fontMenu) {
    fontBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      fontMenu.classList.toggle("open");
    });
    document.addEventListener("click", function (e) {
      if (!fontMenu.contains(e.target) && e.target !== fontBtn) {
        fontMenu.classList.remove("open");
      }
    });
  }

  document.querySelectorAll("[data-theme]").forEach(function (btn) {
    btn.addEventListener("click", function () { applyTheme(btn.getAttribute("data-theme")); });
  });
  document.querySelectorAll("[data-font]").forEach(function (btn) {
    btn.addEventListener("click", function () { applyFont(btn.getAttribute("data-font")); });
  });
  var decBtn = document.getElementById("font-size-dec");
  var incBtn = document.getElementById("font-size-inc");
  if (decBtn) decBtn.addEventListener("click", function () {
    applySize(parseInt(localStorage.getItem("circlizepy_size") || "16", 10) - 1);
  });
  if (incBtn) incBtn.addEventListener("click", function () {
    applySize(parseInt(localStorage.getItem("circlizepy_size") || "16", 10) + 1);
  });

  function loadSearchIndex(cb) {
    if (searchIndex) return cb(searchIndex);
    fetch("assets/search_index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) { searchIndex = data; cb(data); })
      .catch(function () { cb([]); });
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }

  function runSearch(query) {
    var q = (query || "").trim().toLowerCase();
    if (!searchResultsEl) return;
    if (q.length < 2) {
      searchResultsEl.classList.remove("active");
      searchResultsEl.innerHTML = "";
      return;
    }
    loadSearchIndex(function (items) {
      var terms = q.split(/\s+/).filter(Boolean);
      var matches = [];
      items.forEach(function (item) {
        var hay = (item.title + " " + item.text).toLowerCase();
        if (terms.every(function (t) { return hay.indexOf(t) !== -1; })) {
          var idx = item.text.toLowerCase().indexOf(terms[0]);
          var start = Math.max(0, idx - 60);
          var snippet = (start > 0 ? "..." : "") + item.text.slice(start, start + 180) + "...";
          matches.push({ item: item, snippet: snippet });
        }
      });
      var html = "<strong>Search results (" + matches.length + ")</strong>";
      if (matches.length === 0) {
        html += "<p style='margin:6px 0 0;color:var(--text-muted)'>No matching sections found.</p>";
      } else {
        matches.slice(0, 20).forEach(function (m) {
          html += "<div class='search-result-item'><a href='" + escapeHtml(m.item.url) + "'>" +
            escapeHtml(m.item.title) + "</a><div class='search-result-snippet'>" +
            escapeHtml(m.snippet) + "</div></div>";
        });
      }
      searchResultsEl.innerHTML = html;
      searchResultsEl.classList.add("active");
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", function () { runSearch(searchInput.value); });
  }
  if (searchToggleBtn && searchInput) {
    searchToggleBtn.addEventListener("click", function () {
      if (bookEl && window.innerWidth <= 960) {
        bookEl.classList.add("mobile-summary-open");
      } else if (bookEl && bookEl.classList.contains("without-summary")) {
        bookEl.classList.remove("without-summary");
      }
      searchInput.focus();
    });
  }

  document.querySelectorAll(".code-wrapper pre").forEach(function (pre) {
    var wrapper = pre.parentElement;
    var btn = document.createElement("button");
    btn.className = "copy-code-btn";
    btn.type = "button";
    btn.textContent = "Copy";
    btn.addEventListener("click", function () {
      var codeText = pre.innerText || pre.textContent || "";
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(codeText).then(function () {
          btn.textContent = "Copied!";
          setTimeout(function () { btn.textContent = "Copy"; }, 1500);
        });
      }
    });
    wrapper.appendChild(btn);
  });

  document.addEventListener("keydown", function (e) {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "ArrowLeft") {
      var prev = document.querySelector(".navigation-prev");
      if (prev && prev.getAttribute("href")) window.location.href = prev.getAttribute("href");
    } else if (e.key === "ArrowRight") {
      var next = document.querySelector(".navigation-next");
      if (next && next.getAttribute("href")) window.location.href = next.getAttribute("href");
    }
  });
})();
