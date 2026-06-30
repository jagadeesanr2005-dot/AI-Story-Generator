// ---------------------------------------------------------------------------
// AI Story Generator - frontend logic
// ---------------------------------------------------------------------------

const promptInput = document.getElementById('promptInput');
const charCount = document.getElementById('charCount');
const genreSelect = document.getElementById('genreSelect');
const lengthSelect = document.getElementById('lengthSelect');
const errorMessage = document.getElementById('errorMessage');

const generateBtn = document.getElementById('generateBtn');
const generateBtnText = document.getElementById('generateBtnText');
const clearBtn = document.getElementById('clearBtn');

const loadingSection = document.getElementById('loadingSection');
const outputSection = document.getElementById('outputSection');
const storyTitle = document.getElementById('storyTitle');
const storyOutput = document.getElementById('storyOutput');
const wordCountEl = document.getElementById('wordCount');
const readingTimeEl = document.getElementById('readingTime');

const copyBtn = document.getElementById('copyBtn');
const copyMessage = document.getElementById('copyMessage');
const downloadBtn = document.getElementById('downloadBtn');
const favoriteBtn = document.getElementById('favoriteBtn');

const themeToggle = document.getElementById('themeToggle');

const historyList = document.getElementById('historyList');
const favoritesList = document.getElementById('favoritesList');
const historyEmpty = document.getElementById('historyEmpty');
const tabBtns = document.querySelectorAll('.tab-btn');

let currentStory = null; // { title, story, genre, length }
let history = [];        // in-memory list of generated stories this session
let favorites = [];      // in-memory list of favorited stories this session
let typewriterTimer = null;

// ---------------------------------------------------------------------------
// Character counter
// ---------------------------------------------------------------------------
promptInput.addEventListener('input', () => {
  charCount.textContent = promptInput.value.length;
});

// ---------------------------------------------------------------------------
// Suggestion chips
// ---------------------------------------------------------------------------
document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    promptInput.value = chip.dataset.prompt;
    charCount.textContent = promptInput.value.length;
    promptInput.focus();
  });
});

// ---------------------------------------------------------------------------
// Theme toggle (dark / light)
// ---------------------------------------------------------------------------
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Default to light; toggle in-memory only (no localStorage per artifact rules,
// but this is a real Flask app served from disk, not a sandboxed artifact,
// so this still simply lives in a JS variable for the session)
let currentTheme = 'light';
themeToggle.addEventListener('click', () => {
  currentTheme = currentTheme === 'light' ? 'dark' : 'light';
  applyTheme(currentTheme);
});

// ---------------------------------------------------------------------------
// Validation + Generate
// ---------------------------------------------------------------------------
function showError(msg) {
  errorMessage.textContent = msg;
}

function clearError() {
  errorMessage.textContent = '';
}

async function generateStory() {
  const prompt = promptInput.value.trim();
  const genre = genreSelect.value;
  const length = lengthSelect.value;

  if (!prompt) {
    showError('Please enter a story prompt.');
    return;
  }
  clearError();

  generateBtn.disabled = true;
  generateBtnText.textContent = 'Generating...';
  outputSection.classList.add('hidden');
  loadingSection.classList.remove('hidden');

  try {
    const res = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, genre, length })
    });

    const data = await res.json();

    if (!res.ok) {
      showError(data.error || 'Something went wrong. Please try again.');
      loadingSection.classList.add('hidden');
      generateBtn.disabled = false;
      generateBtnText.textContent = '✨ Generate Story';
      return;
    }

    currentStory = data;
    displayStory(data);
    addToHistory(data);

  } catch (err) {
    showError('Could not reach the server. Please make sure the app is running.');
  } finally {
    loadingSection.classList.add('hidden');
    generateBtn.disabled = false;
    generateBtnText.textContent = '✨ Generate Story';
  }
}

generateBtn.addEventListener('click', generateStory);

// Allow Ctrl+Enter to generate from the textarea
promptInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    generateStory();
  }
});

// ---------------------------------------------------------------------------
// Display story with typewriter animation
// ---------------------------------------------------------------------------
function displayStory(data) {
  outputSection.classList.remove('hidden');
  storyTitle.textContent = data.title;
  favoriteBtn.textContent = '🤍 Favorite';
  copyMessage.classList.add('hidden');

  const words = data.story.split(/\s+/).filter(Boolean).length;
  const readingMins = Math.max(1, Math.round(words / 200));
  wordCountEl.textContent = `${words} words`;
  readingTimeEl.textContent = `${readingMins} min read`;

  typewriterEffect(data.story);

  outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function typewriterEffect(text) {
  clearInterval(typewriterTimer);
  storyOutput.textContent = '';
  let i = 0;
  const speed = text.length > 600 ? 4 : 12; // faster reveal for long stories
  typewriterTimer = setInterval(() => {
    storyOutput.textContent += text[i];
    i++;
    if (i >= text.length) {
      clearInterval(typewriterTimer);
    }
  }, speed);
}

// ---------------------------------------------------------------------------
// Copy
// ---------------------------------------------------------------------------
copyBtn.addEventListener('click', async () => {
  if (!currentStory) return;
  try {
    await navigator.clipboard.writeText(currentStory.story);
    copyMessage.textContent = 'Story copied successfully!';
    copyMessage.classList.remove('hidden');
    setTimeout(() => copyMessage.classList.add('hidden'), 2500);
  } catch {
    copyMessage.textContent = 'Could not copy — please copy manually.';
    copyMessage.classList.remove('hidden');
  }
});

// ---------------------------------------------------------------------------
// Download as .txt
// ---------------------------------------------------------------------------
downloadBtn.addEventListener('click', () => {
  if (!currentStory) return;
  const blob = new Blob([`${currentStory.title}\n\n${currentStory.story}`], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${currentStory.title.replace(/\s+/g, '_')}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
});

// ---------------------------------------------------------------------------
// Favorite
// ---------------------------------------------------------------------------
favoriteBtn.addEventListener('click', () => {
  if (!currentStory) return;
  const alreadyFav = favorites.some(f => f.story === currentStory.story);
  if (alreadyFav) {
    favorites = favorites.filter(f => f.story !== currentStory.story);
    favoriteBtn.textContent = '🤍 Favorite';
  } else {
    favorites.unshift({ ...currentStory, id: Date.now() });
    favoriteBtn.textContent = '⭐ Favorited';
  }
  renderFavorites();
});

// ---------------------------------------------------------------------------
// History
// ---------------------------------------------------------------------------
function addToHistory(data) {
  history.unshift({ ...data, id: Date.now() });
  if (history.length > 20) history.pop();
  renderHistory();
}

function renderHistory() {
  historyEmpty.classList.toggle('hidden', history.length > 0);
  historyList.innerHTML = history.map(item => `
    <div class="history-item" data-id="${item.id}">
      <div>
        <div class="hi-title">${escapeHtml(item.title)}</div>
        <div class="hi-genre">${escapeHtml(item.genre)} · ${escapeHtml(item.length)}</div>
      </div>
    </div>
  `).join('');

  historyList.querySelectorAll('.history-item').forEach(el => {
    el.addEventListener('click', () => {
      const id = Number(el.dataset.id);
      const item = history.find(h => h.id === id);
      if (item) {
        currentStory = item;
        displayStory(item);
      }
    });
  });
}

function renderFavorites() {
  favoritesList.innerHTML = favorites.length
    ? favorites.map(item => `
      <div class="history-item" data-id="${item.id}">
        <div>
          <div class="hi-title">${escapeHtml(item.title)}</div>
          <div class="hi-genre">${escapeHtml(item.genre)} · ${escapeHtml(item.length)}</div>
        </div>
        <button class="hi-fav" data-remove="${item.id}">⭐</button>
      </div>
    `).join('')
    : `<p class="empty-text">No favorites yet — click 🤍 Favorite on a story.</p>`;

  favoritesList.querySelectorAll('.history-item').forEach(el => {
    el.addEventListener('click', (e) => {
      if (e.target.dataset.remove) return;
      const id = Number(el.dataset.id);
      const item = favorites.find(h => h.id === id);
      if (item) {
        currentStory = item;
        displayStory(item);
      }
    });
  });

  favoritesList.querySelectorAll('[data-remove]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const id = Number(btn.dataset.remove);
      favorites = favorites.filter(f => f.id !== id);
      renderFavorites();
    });
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// History / Favorites tabs
// ---------------------------------------------------------------------------
tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    tabBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const tab = btn.dataset.tab;
    historyList.classList.toggle('hidden', tab !== 'history');
    favoritesList.classList.toggle('hidden', tab !== 'favorites');
    historyEmpty.classList.toggle('hidden', !(tab === 'history' && history.length === 0));
  });
});

// ---------------------------------------------------------------------------
// Clear
// ---------------------------------------------------------------------------
clearBtn.addEventListener('click', () => {
  promptInput.value = '';
  charCount.textContent = '0';
  genreSelect.selectedIndex = 0;
  lengthSelect.value = 'medium';
  clearError();
  outputSection.classList.add('hidden');
  currentStory = null;
  clearInterval(typewriterTimer);
});

// Initial render
renderHistory();
renderFavorites();
