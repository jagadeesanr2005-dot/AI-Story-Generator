const $ = (id) => document.getElementById(id);
const promptInput = $('promptInput');
const charCount = $('charCount');
const genreSelect = $('genreSelect');
const lengthSelect = $('lengthSelect');
const errorMessage = $('errorMessage');
const statusMessage = $('statusMessage');
const generateBtn = $('generateBtn');
const clearBtn = $('clearBtn');
const outputSection = $('outputSection');
const loadingSection = $('loadingSection');
const storyTitle = $('storyTitle');
const storyOutput = $('storyOutput');
const wordCountEl = $('wordCount');
const readingTimeEl = $('readingTime');
const providerEl = $('providerBadge');
const copyBtn = $('copyBtn');
const downloadBtn = $('downloadBtn');
const downloadJsonBtn = $('downloadJsonBtn');
const favoriteBtn = $('favoriteBtn');
const regenerateBtn = $('regenerateBtn');
const themeToggle = $('themeToggle');
const historyList = $('historyList');
const favoritesList = $('favoritesList');
const historyEmpty = $('historyEmpty');
const tabBtns = document.querySelectorAll('.tab-btn');

const STORAGE_KEY = 'story-generator-v2';
let currentStory = null;
let history = [];
let favorites = [];
let typewriterTimer = null;
let currentTheme = localStorage.getItem('story-theme') || 'light';

const lengthTargets = { short: '250–350 words', medium: '600–800 words', long: '1,100–1,400 words' };

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ history, favorites }));
}
function loadState() {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    history = Array.isArray(data.history) ? data.history : [];
    favorites = Array.isArray(data.favorites) ? data.favorites : [];
  } catch { history = []; favorites = []; }
}
function setTheme(theme) {
  currentTheme = theme;
  document.documentElement.dataset.theme = theme;
  themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
  themeToggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
  localStorage.setItem('story-theme', theme);
}
function setError(message = '') { errorMessage.textContent = message; errorMessage.classList.toggle('visible', !!message); }
function setStatus(message = '') { statusMessage.textContent = message; statusMessage.classList.toggle('visible', !!message); }
function updateCounter() { charCount.textContent = promptInput.value.length; }
function countWords(text) { return text.trim() ? text.trim().split(/\s+/).length : 0; }
function safeFileName(name) { return (name || 'story').replace(/[^a-z0-9-_ ]/gi, '').trim().replace(/\s+/g, '_').slice(0, 80) || 'story'; }
function escapeHtml(value) { const div = document.createElement('div'); div.textContent = value; return div.innerHTML; }

function typewriterEffect(text) {
  clearInterval(typewriterTimer);
  storyOutput.textContent = '';
  let i = 0;
  const speed = text.length > 1800 ? 2 : text.length > 800 ? 4 : 9;
  typewriterTimer = setInterval(() => {
    storyOutput.textContent += text[i++] || '';
    if (i >= text.length) clearInterval(typewriterTimer);
  }, speed);
}

function displayStory(data, animate = true) {
  currentStory = data;
  outputSection.classList.remove('hidden');
  storyTitle.textContent = data.title || 'Untitled Story';
  const words = countWords(data.story || '');
  wordCountEl.textContent = `${words.toLocaleString()} words`;
  readingTimeEl.textContent = `${Math.max(1, Math.ceil(words / 200))} min read`;
  providerEl.textContent = '';
  providerEl.className = `provider-badge ${data.provider === 'local-fallback' ? 'offline' : ''}`;
  favoriteBtn.textContent = isFavorite(data) ? '⭐ Favorited' : '🤍 Favorite';
  if (animate) typewriterEffect(data.story); else storyOutput.textContent = data.story;
  outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function isFavorite(item) { return favorites.some(f => f.id === item.id || f.story === item.story); }

async function generateStory() {
  const prompt = promptInput.value.trim();
  const genre = genreSelect.value;
  const length = lengthSelect.value;
  if (!prompt) return setError('Give your story a starting idea first.');
  if (prompt.length < 3) return setError('Please enter at least a few words.');
  setError(''); setStatus('');
  generateBtn.disabled = true;
  regenerateBtn.disabled = true;
  clearInterval(typewriterTimer);
  outputSection.classList.add('hidden');
  loadingSection.classList.remove('hidden');
  document.querySelector('.loading-detail').textContent = `${lengthTargets[length]} • ${genreSelect.options[genreSelect.selectedIndex].text}`;

  try {
    const response = await fetch('/generate', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, genre, length })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to generate the story.');
    data.id = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());
    history = [data, ...history.filter(x => x.story !== data.story)].slice(0, 30);
    saveState(); renderHistory(); renderFavorites(); displayStory(data);
    if (data.warning) setStatus(data.warning);
  } catch (error) {
    setError(error.message || 'Could not reach the server.');
  } finally {
    loadingSection.classList.add('hidden');
    generateBtn.disabled = false;
    regenerateBtn.disabled = false;
  }
}

function renderHistory() {
  historyEmpty.classList.toggle('hidden', history.length > 0);
  historyList.innerHTML = history.map(item => `
    <button class="history-item" data-id="${escapeHtml(item.id)}">
      <span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.genre)} · ${escapeHtml(item.length)} · ${countWords(item.story)} words</small></span>
      <span>›</span>
    </button>`).join('');
  historyList.querySelectorAll('.history-item').forEach(btn => btn.addEventListener('click', () => {
    const item = history.find(x => x.id === btn.dataset.id);
    if (item) displayStory(item, false);
  }));
}
function renderFavorites() {
  favoritesList.innerHTML = favorites.length ? favorites.map(item => `
    <button class="history-item" data-id="${escapeHtml(item.id)}">
      <span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.genre)} · ${escapeHtml(item.length)}</small></span>
      <span>⭐</span>
    </button>`).join('') : '<p class="empty-text">No favorites yet. Save a story you love.</p>';
  favoritesList.querySelectorAll('.history-item').forEach(btn => btn.addEventListener('click', () => {
    const item = favorites.find(x => x.id === btn.dataset.id);
    if (item) displayStory(item, false);
  }));
}

function downloadBlob(blob, name) {
  const url = URL.createObjectURL(blob); const a = document.createElement('a');
  a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
}

promptInput.addEventListener('input', updateCounter);
document.querySelectorAll('.chip').forEach(chip => chip.addEventListener('click', () => {
  promptInput.value = chip.dataset.prompt; updateCounter(); promptInput.focus();
}));
themeToggle.addEventListener('click', () => setTheme(currentTheme === 'light' ? 'dark' : 'light'));
generateBtn.addEventListener('click', generateStory);
regenerateBtn.addEventListener('click', generateStory);
promptInput.addEventListener('keydown', e => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) generateStory(); });
clearBtn.addEventListener('click', () => {
  promptInput.value = ''; updateCounter(); setError(''); setStatus(''); outputSection.classList.add('hidden'); currentStory = null; clearInterval(typewriterTimer);
});
copyBtn.addEventListener('click', async () => {
  if (!currentStory) return;
  try { await navigator.clipboard.writeText(`${currentStory.title}\n\n${currentStory.story}`); setStatus('Story copied to clipboard.'); setTimeout(() => setStatus(''), 2200); }
  catch { setError('Clipboard access was blocked. You can select and copy the story manually.'); }
});
downloadBtn.addEventListener('click', () => {
  if (!currentStory) return;
  downloadBlob(new Blob([`${currentStory.title}\n\n${currentStory.story}`], { type: 'text/plain;charset=utf-8' }), `${safeFileName(currentStory.title)}.txt`);
});
downloadJsonBtn.addEventListener('click', () => {
  if (!currentStory) return;
  downloadBlob(new Blob([JSON.stringify(currentStory, null, 2)], { type: 'application/json' }), `${safeFileName(currentStory.title)}.json`);
});
favoriteBtn.addEventListener('click', () => {
  if (!currentStory) return;
  if (isFavorite(currentStory)) favorites = favorites.filter(f => f.story !== currentStory.story);
  else favorites.unshift({ ...currentStory });
  saveState(); renderFavorites(); displayStory(currentStory, false);
});
tabBtns.forEach(btn => btn.addEventListener('click', () => {
  tabBtns.forEach(b => b.classList.remove('active')); btn.classList.add('active');
  const fav = btn.dataset.tab === 'favorites'; historyList.classList.toggle('hidden', fav); favoritesList.classList.toggle('hidden', !fav); historyEmpty.classList.toggle('hidden', fav || history.length > 0);
}));

loadState(); setTheme(currentTheme); updateCounter(); renderHistory(); renderFavorites();

// Story translation
const translateLanguage = $('translateLanguage');
const translateBtn = $('translateBtn');
const translationGalaxy = $('translationGalaxy');

function showTranslationGalaxy() {
  if (!translationGalaxy) return;

  translationGalaxy.classList.remove('hidden');
  translationGalaxy.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function hideTranslationGalaxy() {
  if (!translationGalaxy) return;

  translationGalaxy.classList.add('hidden');
  translationGalaxy.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

// async function translateCurrentStory() {
//   if (!currentStory) return;

//   const language = translateLanguage.value;

//   if (language === 'english') {
//     setStatus('The story is already in English.');
//     return;
//   }

//   translateBtn.disabled = true;
//   setError('');
//   setStatus('Translating your story...');
//   showTranslationGalaxy();

//   try {
//     const response = await fetch('/translate', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json'
//       },
//       body: JSON.stringify({
//         title: currentStory.title,
//         story: currentStory.story,
//         language
//       })
//     });

//     const data = await response.json();

//     if (!response.ok) {
//       throw new Error(data.error || 'Translation failed.');
//     }

//     const translated = {
//       ...currentStory,
//       title: data.title,
//       story: data.story,
//       translatedFrom: currentStory.title,
//       language: data.language,
//       provider: data.provider
//     };

//     translated.id = crypto.randomUUID
//       ? crypto.randomUUID()
//       : String(Date.now());

//     currentStory = translated;

//     history = [
//       translated,
//       ...history.filter(x => x.story !== translated.story)
//     ].slice(0, 30);

//     saveState();
//     renderHistory();
//     renderFavorites();
//     displayStory(translated, true);

//     setStatus(`Translated to ${data.language}.`);

//   } catch (error) {
//     setError(error.message || 'Translation failed.');
//     setStatus('');

//   } finally {
//     translateBtn.disabled = false;
//     hideTranslationGalaxy();
//   }
// }

async function translateCurrentStory() {
  if (!currentStory) return;

  const language = translateLanguage.value;

  if (language === 'english') {
    translateBtn.disabled = true;
    setError('');
    setStatus('Restoring original English story...');
    showTranslationGalaxy();

    try {
      await new Promise(resolve => setTimeout(resolve, 700));

      if (currentStory.originalStory) {
        const restoredStory = {
          ...currentStory,
          title: currentStory.originalTitle,
          story: currentStory.originalStory,
          language: 'english'
        };

        delete restoredStory.originalTitle;
        delete restoredStory.originalStory;

        restoredStory.id = crypto.randomUUID
          ? crypto.randomUUID()
          : String(Date.now());

        currentStory = restoredStory;

        history = [
          restoredStory,
          ...history.filter(x => x.story !== restoredStory.story)
        ].slice(0, 30);

        saveState();
        renderHistory();
        renderFavorites();
        displayStory(restoredStory, true);

        setStatus('Original English story restored.');
      } else {
        setStatus('The story is already in English.');
      }

    } catch (error) {
      setError(error.message || 'Could not restore the English story.');
      setStatus('');

    } finally {
      translateBtn.disabled = false;
      hideTranslationGalaxy();
    }

    return;
  }

  translateBtn.disabled = true;
  setError('');
  setStatus('Translating your story...');
  showTranslationGalaxy();

  try {
    const response = await fetch('/translate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: currentStory.title,
        story: currentStory.story,
        language
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Translation failed.');
    }

    const originalTitle =
      currentStory.originalTitle || currentStory.title;

    const originalStory =
      currentStory.originalStory || currentStory.story;

    const translated = {
      ...currentStory,

      title: data.title,
      story: data.story,

      originalTitle: originalTitle,
      originalStory: originalStory,

      language: data.language,
      provider: data.provider
    };

    translated.id = crypto.randomUUID
      ? crypto.randomUUID()
      : String(Date.now());

    currentStory = translated;

    history = [
      translated,
      ...history.filter(x => x.story !== translated.story)
    ].slice(0, 30);

    saveState();
    renderHistory();
    renderFavorites();
    displayStory(translated, true);

    setStatus(`Translated to ${data.language}.`);

  } catch (error) {
    setError(error.message || 'Translation failed.');
    setStatus('');

  } finally {
    translateBtn.disabled = false;
    hideTranslationGalaxy();
  }
}

translateBtn.addEventListener('click', translateCurrentStory);