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

  var galleryLightbox = document.getElementById("gallery-lightbox");

  // Interactive Figure Gallery filtering & lightbox
  var galleryGrid = document.getElementById("gallery-grid");
  if (galleryGrid) {
    var activePart = "all";
    var activeChapter = "all";
    var gallerySearchInput = document.getElementById("gallery-search-input");
    var visibleCountEl = document.getElementById("gallery-visible-count");
    var toggleCodeBtn = document.getElementById("gallery-toggle-code");
    var cards = Array.prototype.slice.call(galleryGrid.querySelectorAll(".gallery-card"));
    var tableRows = Array.prototype.slice.call(document.querySelectorAll("#gallery-index-table tbody tr"));
    var partPills = Array.prototype.slice.call(document.querySelectorAll("[data-filter-part]"));
    var chapterPills = Array.prototype.slice.call(document.querySelectorAll("[data-filter-chapter]"));

    function applyGalleryFilters() {
      var q = gallerySearchInput ? gallerySearchInput.value.trim().toLowerCase() : "";
      var terms = q ? q.split(/\s+/).filter(Boolean) : [];
      var shown = 0;

      function matches(el) {
        var partOk = activePart === "all" || el.getAttribute("data-part") === activePart;
        var chOk = activeChapter === "all" || el.getAttribute("data-chapter") === activeChapter;
        if (!partOk || !chOk) return false;
        if (terms.length === 0) return true;
        var hay = (el.getAttribute("data-search") || "").toLowerCase();
        return terms.every(function (t) { return hay.indexOf(t) !== -1; });
      }

      cards.forEach(function (card) {
        var ok = matches(card);
        card.hidden = !ok;
        if (ok) shown += 1;
      });
      tableRows.forEach(function (row) {
        row.hidden = !matches(row);
      });

      if (visibleCountEl) {
        visibleCountEl.textContent = "Showing " + shown + " of " + cards.length + " figures";
      }
    }

    partPills.forEach(function (btn) {
      btn.addEventListener("click", function () {
        activePart = btn.getAttribute("data-filter-part") || "all";
        partPills.forEach(function (b) { b.classList.toggle("active", b === btn); });
        applyGalleryFilters();
      });
    });

    chapterPills.forEach(function (btn) {
      btn.addEventListener("click", function () {
        activeChapter = btn.getAttribute("data-filter-chapter") || "all";
        chapterPills.forEach(function (b) { b.classList.toggle("active", b === btn); });
        applyGalleryFilters();
      });
    });

    if (gallerySearchInput) {
      gallerySearchInput.addEventListener("input", applyGalleryFilters);
    }

    document.querySelectorAll(".api-pill[data-api]").forEach(function (pill) {
      pill.addEventListener("click", function () {
        if (!gallerySearchInput) return;
        var api = pill.getAttribute("data-api") || "";
        if (gallerySearchInput.value.trim().toLowerCase() === api.toLowerCase()) {
          gallerySearchInput.value = "";
        } else {
          gallerySearchInput.value = api;
        }
        applyGalleryFilters();
      });
    });

    if (toggleCodeBtn) {
      var codeExpanded = false;
      toggleCodeBtn.addEventListener("click", function () {
        codeExpanded = !codeExpanded;
        cards.forEach(function (card) {
          if (!card.hidden) {
            var det = card.querySelector(".gallery-code-details");
            if (det) det.open = codeExpanded;
          }
        });
        toggleCodeBtn.textContent = codeExpanded ? "Collapse All Code" : "Expand All Code";
      });
    }

    // Lightbox modal
    if (galleryLightbox) {
      var lbImg = document.getElementById("lightbox-img");
      var lbBadge = document.getElementById("lightbox-badge");
      var lbCaption = document.getElementById("lightbox-caption");
      var lbOpenChapter = document.getElementById("lightbox-open-chapter");
      var lbClose = document.getElementById("lightbox-close");
      var lbPrev = document.getElementById("lightbox-prev");
      var lbNext = document.getElementById("lightbox-next");
      var lbActiveIndex = -1;

      function visibleThumbButtons() {
        return cards
          .filter(function (c) { return !c.hidden; })
          .map(function (c) { return c.querySelector(".gallery-thumb-btn"); })
          .filter(Boolean);
      }

      function showLightboxAt(idx) {
        var btns = visibleThumbButtons();
        if (!btns.length) return;
        if (idx < 0) idx = btns.length - 1;
        if (idx >= btns.length) idx = 0;
        lbActiveIndex = idx;
        var btn = btns[idx];
        var src = btn.getAttribute("data-full-src") || "";
        var badge = btn.getAttribute("data-fig-badge") || "";
        var cap = btn.getAttribute("data-caption") || "";
        var chUrl = btn.getAttribute("data-chapter-url") || "index.html";
        var chLbl = btn.getAttribute("data-chapter-label") || "Chapter";
        if (lbImg) {
          lbImg.src = src;
          lbImg.alt = badge + ": " + cap;
        }
        if (lbBadge) lbBadge.textContent = badge + " (" + (idx + 1) + "/" + btns.length + ")";
        if (lbCaption) lbCaption.textContent = cap;
        if (lbOpenChapter) {
          lbOpenChapter.href = chUrl;
          lbOpenChapter.textContent = "Open in " + chLbl + " \u2192";
        }
        galleryLightbox.hidden = false;
      }

      function closeLightbox() {
        galleryLightbox.hidden = true;
      }

      galleryGrid.addEventListener("click", function (e) {
        var btn = e.target.closest ? e.target.closest(".gallery-thumb-btn") : null;
        if (!btn) return;
        var btns = visibleThumbButtons();
        var idx = btns.indexOf(btn);
        showLightboxAt(idx >= 0 ? idx : 0);
      });

      if (lbClose) lbClose.addEventListener("click", closeLightbox);
      if (lbPrev) lbPrev.addEventListener("click", function () { showLightboxAt(lbActiveIndex - 1); });
      if (lbNext) lbNext.addEventListener("click", function () { showLightboxAt(lbActiveIndex + 1); });
      galleryLightbox.addEventListener("click", function (e) {
        if (e.target === galleryLightbox) closeLightbox();
      });
      document.addEventListener("keydown", function (e) {
        if (galleryLightbox.hidden) return;
        if (e.key === "Escape") {
          closeLightbox();
        } else if (e.key === "ArrowLeft") {
          e.preventDefault();
          showLightboxAt(lbActiveIndex - 1);
        } else if (e.key === "ArrowRight") {
          e.preventDefault();
          showLightboxAt(lbActiveIndex + 1);
        }
      });
    }
  }

  document.addEventListener("keydown", function (e) {
    if (galleryLightbox && !galleryLightbox.hidden) return;
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
