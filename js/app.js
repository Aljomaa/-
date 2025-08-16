(function () {
  const page = document.body.getAttribute("data-page");
  const config = window.TI_CONFIG || {};
  const reciters = window.RECITERS || [];
  const surahs = window.SURAHS || [];
  const trending = window.TRENDING || [];
  const articles = window.ARTICLES || [];

  function $(sel) { return document.querySelector(sel); }
  function $all(sel) { return Array.from(document.querySelectorAll(sel)); }

  function getReciterById(id) {
    return reciters.find(r => r.id === id) || reciters[0];
  }

  function buildAudioUrl(reciterId, surahId, quality) {
    const q = quality || 128;
    const sid = String(surahId).padStart(3, '0');
    return `${config.baseAudio}/${reciterId}/${q}/${sid}.mp3`;
  }

  function createReciterAvatar(name) {
    const initials = name.split(" ").map(p => p[0]).filter(Boolean).slice(0, 2).join("");
    const div = document.createElement('div');
    div.className = 'reciter-avatar';
    div.textContent = initials;
    return div;
  }

  function renderHomepage() {
    const grid = $("#reciters-grid");
    if (grid) {
      grid.innerHTML = reciters.slice(0, 6).map(r => {
        return `<a href="/listen.html?reciter=${r.id}" class="card reciter-card" aria-label="${r.name}">
          <div class="reciter-avatar" aria-hidden="true">${r.name.split(' ').map(n=>n[0]).slice(0,2).join('')}</div>
          <div class="reciter-meta">
            <div class="name">${r.name}</div>
            <div class="country">${r.country}</div>
          </div>
        </a>`;
      }).join("");
    }

    const slider = $("#trending-surahs");
    if (slider) {
      slider.innerHTML = trending.map(id => {
        const s = surahs.find(x => x.id === id);
        if (!s) return '';
        return `<a class="surah-pill" href="/listen.html?surah=${s.id}">
          <div class="title">${s.name}</div>
          <div class="meta">${s.type === 'meccan' ? 'مكية' : 'مدنية'} • ${s.ayahs} آية</div>
        </a>`;
      }).join("");
    }
  }

  function renderListenPage() {
    const listEl = $("#surahsList");
    if (!listEl) return;

    const reciterSelect = $("#reciterSelect");
    const classificationSelect = $("#classificationSelect");
    const searchInput = $("#searchInput");

    const url = new URL(window.location.href);
    const initialReciter = url.searchParams.get('reciter') || reciters[0]?.id;
    const initialSurahId = Number(url.searchParams.get('surah')) || null;

    reciterSelect.innerHTML = reciters.map(r => `<option value="${r.id}">${r.name}</option>`).join("");
    if (initialReciter) reciterSelect.value = initialReciter;

    function filteredSurahs() {
      const q = (searchInput.value || '').trim();
      let items = surahs.slice();
      const cls = classificationSelect.value;
      if (cls === 'meccan' || cls === 'medinan') {
        items = items.filter(s => s.type === cls);
      }
      if (cls === 'byalpha') {
        items.sort((a,b)=> a.name.localeCompare(b.name));
      }
      if (cls === 'bylength') {
        items.sort((a,b)=> a.ayahs - b.ayahs);
      }
      if (q) {
        items = items.filter(s => s.name.includes(q));
      }
      return items;
    }

    function renderList() {
      const items = filteredSurahs();
      listEl.innerHTML = items.map(s => {
        const slug = buildAudioUrl(reciterSelect.value, s.id, 128);
        return `<div class="surah-row">
          <span class="badge">${String(s.id).padStart(3,'0')}</span>
          <div>
            <div class="title">${s.name}</div>
            <div class="meta">${s.type === 'meccan' ? 'مكية' : 'مدنية'} • ${s.ayahs} آية</div>
          </div>
          <button class="btn play-btn" data-surah="${s.id}">تشغيل</button>
          <a class="btn btn-outline" href="${slug}" download>تحميل</a>
        </div>`;
      }).join("");
    }

    renderList();

    [reciterSelect, classificationSelect].forEach(el => el.addEventListener('change', renderList));
    searchInput.addEventListener('input', renderList);

    const audio = $("#globalAudio");
    const nowPlaying = $("#nowPlaying");
    const playPauseBtn = $("#playPauseBtn");
    const nextBtn = $("#nextBtn");
    const prevBtn = $("#prevBtn");

    let currentIndex = 0;

    function currentList() { return filteredSurahs(); }

    function playSurahById(id) {
      const items = currentList();
      const idx = items.findIndex(s => s.id === id);
      if (idx >= 0) {
        currentIndex = idx;
        const s = items[idx];
        const src = buildAudioUrl(reciterSelect.value, s.id, 128);
        audio.src = src;
        audio.play().catch(()=>{});
        nowPlaying.textContent = `يتم التشغيل: ${s.name} — ${getReciterById(reciterSelect.value).name}`;
        playPauseBtn.textContent = '⏸️';
      }
    }

    function playAt(idx) {
      const items = currentList();
      if (idx < 0 || idx >= items.length) return;
      const s = items[idx];
      currentIndex = idx;
      const src = buildAudioUrl(reciterSelect.value, s.id, 128);
      audio.src = src;
      audio.play().catch(()=>{});
      nowPlaying.textContent = `يتم التشغيل: ${s.name} — ${getReciterById(reciterSelect.value).name}`;
      playPauseBtn.textContent = '⏸️';
    }

    listEl.addEventListener('click', (e) => {
      const btn = e.target.closest('.play-btn');
      if (!btn) return;
      const sid = Number(btn.getAttribute('data-surah'));
      playSurahById(sid);
    });

    playPauseBtn.addEventListener('click', () => {
      if (audio.paused) {
        audio.play().catch(()=>{});
        playPauseBtn.textContent = '⏸️';
      } else {
        audio.pause();
        playPauseBtn.textContent = '▶️';
      }
    });

    nextBtn.addEventListener('click', () => { playAt(currentIndex + 1); });
    prevBtn.addEventListener('click', () => { playAt(currentIndex - 1); });

    if (initialSurahId) playSurahById(initialSurahId);
  }

  function renderDownloadPage() {
    const kitsEl = $("#downloadKits");
    if (!kitsEl) return;

    function kitHtml(reciter) {
      const qLinks = reciter.quality.map(q => {
        const full = `${config.downloadBase}/${reciter.id}/${q}/quran-${reciter.id}-${q}kbps.zip`;
        const juz = `${config.downloadBase}/${reciter.id}/${q}/juz-${reciter.id}-${q}kbps.zip`;
        const hizb = `${config.downloadBase}/${reciter.id}/${q}/hizb-${reciter.id}-${q}kbps.zip`;
        const amma = `${config.downloadBase}/${reciter.id}/${q}/amma-${reciter.id}-${q}kbps.zip`;
        return `<div class="kit">
          <div><strong>${reciter.name}</strong> — ${q}kbps</div>
          <div class="actions">
            <a class="btn btn-primary" href="${full}">المصحف كامل</a>
            <a class="btn" href="${juz}">الأجزاء</a>
            <a class="btn" href="${hizb}">الأحزاب</a>
            <a class="btn" href="${amma}">جزء عم</a>
          </div>
        </div>`;
      }).join("");
      return qLinks;
    }

    kitsEl.innerHTML = reciters.map(kitHtml).join("");
  }

  function renderRecitersPage() {
    const grid = $("#recitersPageGrid");
    if (!grid) return;
    grid.innerHTML = reciters.map(r => {
      return `<div class="card reciter-card">
        <div class="reciter-avatar" aria-hidden="true">${r.name.split(' ').map(n=>n[0]).slice(0,2).join('')}</div>
        <div class="reciter-meta">
          <div class="name">${r.name}</div>
          <div class="country">${r.country}</div>
          <div class="mt-2"><a class="btn btn-outline" href="/listen.html?reciter=${r.id}">الاستماع لتلاواته</a></div>
        </div>
      </div>`;
    }).join("");
  }

  function renderArticlesPage() {
    const grid = $("#articlesGrid");
    if (!grid) return;
    grid.innerHTML = articles.map(a => {
      return `<a class="card article-card" href="${a.url}">
        <h3>${a.title}</h3>
        <p>${a.excerpt}</p>
      </a>`;
    }).join("");
  }

  function renderPodcastsPage() {
    const grid = $("#podcastsGrid");
    if (!grid) return;
    const seriesList = window.PODCASTS || [];
    const base = (window.TI_CONFIG && window.TI_CONFIG.podcastBase) || '';
    grid.innerHTML = seriesList.map(series => {
      const eps = (series.episodes || []).map(ep => {
        const audioUrl = `${base}/${encodeURIComponent(ep.audio)}`;
        return `<div class="card podcast-card">
          <div class="podcast-meta">
            <div class="title">${ep.title}</div>
            <div class="meta">المدة: ${ep.duration}</div>
          </div>
          <audio preload="none" controls src="${audioUrl}"></audio>
        </div>`;
      }).join("");
      return `<div class="podcast-series">
        <h3 class="series-title">${series.series}</h3>
        <div class="grid">${eps}</div>
      </div>`;
    }).join("");
  }

  function setYear() {
    const y = new Date().getFullYear();
    const el = $("#year");
    if (el) el.textContent = y;
  }

  function init() {
    setYear();
    if (page === 'home') renderHomepage();
    if (page === 'listen') renderListenPage();
    if (page === 'download') renderDownloadPage();
    if (page === 'reciters') renderRecitersPage();
    if (page === 'articles') renderArticlesPage();
    if (page === 'podcasts') renderPodcastsPage();
  }

  document.addEventListener('DOMContentLoaded', init);
})();