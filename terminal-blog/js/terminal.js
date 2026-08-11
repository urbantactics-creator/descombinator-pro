/* ═══════════════════════════════════════════
   TERMINAL BLOG — CORE ENGINE
   ═══════════════════════════════════════════ */

(() => {
  'use strict';

  // ── STATE ──
  const state = {
    cwd: '~',
    history: [],
    historyIndex: -1,
    soundEnabled: false,
    crtEnabled: true,
    files: {
      '~': {
        type: 'dir',
        children: {
          'posts': { type: 'dir', children: {} },
          'projects': { type: 'dir', children: {} },
          'about.md': { type: 'file', content: 'about' },
          'contact.md': { type: 'file', content: 'contact' },
          'readme.md': { type: 'file', content: 'readme' }
        }
      }
    },
    posts: {
      'hello-world.md': {
        title: 'Hello, World!',
        date: '2026-08-11',
        tags: ['intro'],
        content: `# Hello, World!

Welcome to my terminal-style blog. This is a space for thoughts on code, systems, and the craft of building software.

## Why a terminal?

Because the command line is honest. No distractions, no tracking pixels, just text and intent.

## What to expect

- Deep dives into low-level systems
- Opinionated takes on tooling and workflows
- Occasional poetry in \`C\` and \`Python\``
      `
      },
      'the-art-of-debugging.md': {
        title: 'The Art of Debugging',
        date: '2026-08-09',
        tags: ['debugging', 'craft'],
        content: `# The Art of Debugging

Debugging is not just finding bugs. It is understanding the system well enough to predict its failures.

## The mindset

- Reproduce first, fix later
- Read the logs before adding print statements
- Form a hypothesis, then test it

## Tools of the trade

| Tool | Purpose |
|------|---------|
| \`gdb\` | Low-level inspection |
| \`strace\` | System call tracing |
| \`wireshark\` | Network archaeology |
| \`printf\` | The original debugger |`
      },
      'building-clis-that-dont-suck.md': {
        title: 'Building CLIs That Don\'t Suck',
        date: '2026-08-05',
        tags: ['cli', 'ux'],
        content: `# Building CLIs That Don't Suck

Most CLIs are built for machines, not humans. Let's fix that.

## Principles

1. **Predictable output** — machines parse it, humans read it
2. **Progressive disclosure** — simple by default, powerful when needed
3. **Composability** — pipes and redirects are features, not hacks

## The forgotten art of help text

\`\`\`
$ mytool --help
USAGE
  mytool [OPTIONS] <input>

OPTIONS
  -o, --output FILE    Write result to FILE
  -v, --verbose        Enable debug logging
  -h, --help           Show this message
\`\`\``
      }
    }
  };

  // ── DOM REFS ──
  const output = document.getElementById('output');
  const input = document.getElementById('command-input');
  const promptEl = document.querySelector('.prompt');
  const cursor = document.getElementById('cursor');
  const ghostText = document.getElementById('ghost-text');
  const crtToggle = document.getElementById('crt-toggle');
  const soundToggle = document.getElementById('sound-toggle');
  const crtOverlay = document.getElementById('crt-overlay');

  // ── PERSISTENCE ──
  function loadHistory() {
    try {
      const saved = sessionStorage.getItem('terminal-blog-history');
      if (saved) {
        state.history = JSON.parse(saved);
        state.historyIndex = state.history.length;
      }
    } catch (e) {
      // ignore
    }
  }

  function saveHistory() {
    try {
      sessionStorage.setItem('terminal-blog-history', JSON.stringify(state.history));
    } catch (e) {
      // ignore
    }
  }

  loadHistory();

  // ── AUDIO ENGINE ──
  let audioCtx = null;

  function initAudio() {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  function playKeySound() {
    if (!state.soundEnabled || !audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.frequency.value = 800 + Math.random() * 400;
    osc.type = 'square';
    gain.gain.value = 0.015;
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.05);
  }

  function playEnterSound() {
    if (!state.soundEnabled || !audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.frequency.value = 440;
    osc.type = 'square';
    gain.gain.value = 0.02;
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.08);
  }

  // ── RENDER HELPERS ──
  function print(text, type = '') {
    const line = document.createElement('div');
    line.className = `terminal-line ${type}`;
    line.innerHTML = escapeHtml(text);
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  // Basic markdown renderer — safe for our static posts
  function simpleMarkdown(text) {
    let html = escapeHtml(text);
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
    html = html.replace(/^- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    html = html.replace(/^&gt; (.*$)/gim, '<blockquote>$1</blockquote>');
    html = html.replace(/\|(.+)\|/g, (match) => {
      const cells = match.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
      return `<tr>${cells}</tr>`;
    });
    html = html.replace(/\n\n/g, '</p><p>');
    html = `<p>${html}</p>`;
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<h[123]>)/g, '$1');
    html = html.replace(/(<\/h[123]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<pre>)/g, '$1');
    html = html.replace(/(<\/pre>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ul>)/g, '$1');
    html = html.replace(/(<\/ul>)<\/p>/g, '$1');
    html = html.replace(/<p>(<blockquote>)/g, '$1');
    html = html.replace(/(<\/blockquote>)<\/p>/g, '$1');
    return html;
  }

  // ── PROMPT HELPERS ──
  function updatePrompt() {
    const display = state.cwd === '~' ? '~' : state.cwd.replace(/^~\//, '~/');
    promptEl.textContent = `guest@blog:${display}$`;
    updateCursorPosition();
  }

  function updateCursorPosition() {
    const promptWidth = promptEl.offsetWidth || promptEl.textContent.length * 0.6;
    const charWidth = 0.6; // approximate rem per char for monospace
    cursor.style.left = `${promptWidth + 0.5 + input.value.length * charWidth}rem`;
  }

  // ── FILESYSTEM HELPERS ──
  function resolvePath(path) {
    if (path === '~') return state.files['~'];
    const parts = path.replace(/^~\//, '').split('/').filter(Boolean);
    let current = state.files['~'];
    for (const part of parts) {
      if (!current || current.type !== 'dir') return null;
      current = current.children[part];
    }
    return current;
  }

  function getCurrentDir() {
    if (state.cwd === '~') return state.files['~'];
    return resolvePath(state.cwd) || state.files['~'];
  }

  function formatListing(dir) {
    if (!dir || dir.type !== 'dir') return '';
    const entries = Object.entries(dir.children);
    if (entries.length === 0) return '(empty directory)';
    return entries.map(([name, node]) => {
      if (node.type === 'dir') return `\u001b[34m${name}/\u001b[0m`;
      return name;
    }).join('  ');
  }

  // ── COMMANDS ──
  const commands = {
    help() {
      const manPage = document.createElement('div');
      manPage.className = 'man-page';
      manPage.innerHTML = `
        <h1>BLOG-CLI(1)</h1>
        <div class="man-section">
          <div class="man-section-title">NAME</div>
          <div>blog-cli — navigate this developer blog via terminal commands</div>
        </div>
        <div class="man-section">
          <div class="man-section-title">SYNOPSIS</div>
          <div class="man-option"><span class="man-option-code">ls [path]</span><span class="man-option-desc">List posts and directories</span></div>
          <div class="man-option"><span class="man-option-code">cat &lt;file&gt;</span><span class="man-option-desc">Read a post or file</span></div>
          <div class="man-option"><span class="man-option-code">cd &lt;dir&gt;</span><span class="man-option-desc">Change to a topic directory</span></div>
          <div class="man-option"><span class="man-option-code">whoami</span><span class="man-option-desc">About the author</span></div>
          <div class="man-option"><span class="man-option-code">mail &lt;addr&gt;</span><span class="man-option-desc">Open contact composer</span></div>
          <div class="man-option"><span class="man-option-code">clear</span><span class="man-option-desc">Clear the terminal</span></div>
          <div class="man-option"><span class="man-option-code">help</span><span class="man-option-desc">Show this manual</span></div>
        </div>
        <div class="man-section">
          <div class="man-section-title">EXAMPLES</div>
          <div class="man-option"><span class="man-option-code">ls posts</span><span class="man-option-desc">List all blog posts</span></div>
          <div class="man-option"><span class="man-option-code">cat posts/hello-world.md</span><span class="man-option-desc">Read a post</span></div>
          <div class="man-option"><span class="man-option-code">cd projects</span><span class="man-option-desc">Filter by projects topic</span></div>
        </div>
      `;
      output.appendChild(manPage);
      output.scrollTop = output.scrollHeight;
    },

    ls(args) {
      const target = args[0] || '.';
      const dir = target === '.' ? getCurrentDir() : resolvePath(state.cwd === '~' ? target : `${state.cwd}/${target}`);
      if (!dir) {
        print(`ls: cannot access '${target}': No such file or directory`, 'error');
        return;
      }
      if (dir.type !== 'dir') {
        print(target, '');
        return;
      }
      print(formatListing(dir), '');
    },

    cat(args) {
      if (!args.length) {
        print('cat: missing file operand', 'error');
        return;
      }
      const target = args[0];
      if (state.posts[target]) {
        const post = state.posts[target];
        const container = document.createElement('div');
        container.className = 'post-content';
        container.innerHTML = simpleMarkdown(post.content);
        output.appendChild(container);
        output.scrollTop = output.scrollHeight;
        return;
      }
      const file = resolvePath(state.cwd === '~' ? target : `${state.cwd}/${target}`);
      if (!file) {
        print(`cat: ${target}: No such file or directory`, 'error');
        return;
      }
      if (file.type === 'dir') {
        print(`cat: ${target}: Is a directory`, 'error');
        return;
      }
      const contentKey = file.content;
      if (contentKey === 'about') {
        const container = document.createElement('div');
        container.className = 'post-content';
        container.innerHTML = simpleMarkdown(`# About

I'm a developer who builds systems, writes code, and occasionally ships products.

## Interests

- Low-level systems programming
- CLI/UX design
- Open source tooling
- Retro computing

## Stack

Currently working with \`C\`, \`Python\`, \`Rust\`, and \`TypeScript\`.`);
        output.appendChild(container);
      } else if (contentKey === 'contact') {
        const container = document.createElement('div');
        container.className = 'contact-form';
        container.innerHTML = `
          <label for="mail-to">To:</label>
          <input type="email" id="mail-to" placeholder="your@email.com..." autocomplete="email">
          <label for="mail-subject">Subject:</label>
          <input type="text" id="mail-subject" placeholder="What's this about?">
          <label for="mail-body">Message:</label>
          <textarea id="mail-body" placeholder="Write your message here..."></textarea>
          <button id="send-mail" type="button">Send</button>
        `;
        output.appendChild(container);
        document.getElementById('send-mail').addEventListener('click', () => {
          const to = document.getElementById('mail-to').value;
          const subject = document.getElementById('mail-subject').value;
          print(`📧 Message queued for ${to || 'recipient'}: "${subject || '(no subject)'}"`, 'success');
        });
      } else if (contentKey === 'readme') {
        const container = document.createElement('div');
        container.className = 'post-content';
        container.innerHTML = simpleMarkdown(`# README

This is a terminal-style developer blog. Type \`help\` to see available commands.`);
        output.appendChild(container);
      } else {
        print(file.content || '(empty file)', '');
      }
      output.scrollTop = output.scrollHeight;
    },

    cd(args) {
      if (!args.length) {
        state.cwd = '~';
        updatePrompt();
        return;
      }
      const target = args[0];
      if (target === '~' || target === '/') {
        state.cwd = '~';
        updatePrompt();
        return;
      }
      const dir = resolvePath(state.cwd === '~' ? target : `${state.cwd}/${target}`);
      if (!dir || dir.type !== 'dir') {
        print(`cd: ${target}: No such directory`, 'error');
        return;
      }
      state.cwd = state.cwd === '~' ? target : `${state.cwd}/${target}`;
      updatePrompt();
    },

    whoami() {
      const container = document.createElement('div');
      container.className = 'post-content';
      container.innerHTML = simpleMarkdown(`# Whoami

**Role:** Developer / Systems thinker
**Location:** /home/guest
**Shell:** zsh
**Editor:** neovim

> "The terminal is the ultimate interface: text in, text out, infinite composability."`);
      output.appendChild(container);
      output.scrollTop = output.scrollHeight;
    },

    mail(args) {
      if (!args.length) {
        print('Usage: mail <address>', 'warning');
        return;
      }
      const addr = args[0];
      const container = document.createElement('div');
      container.className = 'contact-form';
      container.innerHTML = `
        <label for="mail-to">To:</label>
        <input type="email" value="${escapeHtml(addr)}" id="mail-to" autocomplete="email">
        <label for="mail-subject">Subject:</label>
        <input type="text" id="mail-subject" placeholder="What's this about?">
        <label for="mail-body">Message:</label>
        <textarea id="mail-body" placeholder="Write your message here..."></textarea>
        <button id="send-mail" type="button">Send</button>
      `;
      output.appendChild(container);
      document.getElementById('send-mail').addEventListener('click', () => {
        const to = document.getElementById('mail-to').value;
        const subject = document.getElementById('mail-subject').value;
        print(`📧 Message queued for ${to || 'recipient'}: "${subject || '(no subject)'}"`, 'success');
      });
      output.scrollTop = output.scrollHeight;
    },

    clear() {
      output.innerHTML = '';
    }
  };

  // ── COMMAND EXECUTION ──
  function executeCommand(raw) {
    const trimmed = raw.trim();
    if (!trimmed) return;

    print(`➜  ${state.cwd === '~' ? '~' : state.cwd.replace(/^~\//, '~/')}$ ${trimmed}`, 'command');

    const parts = trimmed.split(/\s+/);
    const cmd = parts[0].toLowerCase();
    const args = parts.slice(1);

    if (commands[cmd]) {
      commands[cmd](args);
    } else {
      print(`command not found: ${cmd}`, 'error');
      print(`Type 'help' for available commands.`, 'info');
    }
  }

  // ── TAB COMPLETION ──
  function getCompletions(partial) {
    const all = [
      'help', 'clear', 'ls', 'cat', 'cd', 'whoami', 'mail',
      'posts', 'projects', 'about.md', 'contact.md', 'readme.md',
      ...Object.keys(state.posts)
    ];
    const lower = partial.toLowerCase();
    return all.filter(c => c.startsWith(lower));
  }

  function updateGhostText(value) {
    const completions = getCompletions(value);
    if (completions.length === 1) {
      ghostText.textContent = completions[0].slice(value.length);
    } else if (completions.length > 1) {
      ghostText.textContent = completions.slice(0, 3).join('  ').slice(value.length);
    } else {
      ghostText.textContent = '';
    }
  }

  // ── EVENT HANDLERS ──
  input.addEventListener('input', () => {
    updateCursorPosition();
    updateGhostText(input.value);
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const value = input.value;
      state.history.push(value);
      state.historyIndex = state.history.length;
      saveHistory();
      playEnterSound();
      executeCommand(value);
      input.value = '';
      updatePrompt();
      ghostText.textContent = '';
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (state.historyIndex > 0) {
        state.historyIndex--;
        input.value = state.history[state.historyIndex];
        updatePrompt();
        ghostText.textContent = '';
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (state.historyIndex < state.history.length - 1) {
        state.historyIndex++;
        input.value = state.history[state.historyIndex];
      } else {
        state.historyIndex = state.history.length;
        input.value = '';
      }
      updatePrompt();
      ghostText.textContent = '';
    } else if (e.key === 'Tab') {
      e.preventDefault();
      const value = input.value;
      const completions = getCompletions(value);
      if (completions.length === 1) {
        input.value = completions[0];
        updatePrompt();
        ghostText.textContent = '';
      } else if (completions.length > 1) {
        print(value + '\t' + completions.join('  '), '');
      }
    } else if (e.key === 'l' && e.ctrlKey) {
      e.preventDefault();
      commands.clear();
    } else if (e.key === 'Backspace') {
      // Ensure cursor and ghost update synchronously after deletion
      requestAnimationFrame(() => {
        updateCursorPosition();
        updateGhostText(input.value);
      });
    } else {
      playKeySound();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (document.activeElement !== input && e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
      input.focus();
    }
  });

  // ── CRT TOGGLE ──
  crtToggle.addEventListener('click', () => {
    state.crtEnabled = !state.crtEnabled;
    crtOverlay.classList.toggle('hidden', !state.crtEnabled);
    crtToggle.classList.toggle('active', state.crtEnabled);
    crtToggle.textContent = state.crtEnabled ? 'CRT' : 'CRT OFF';
  });
  crtToggle.classList.add('active');

  // ── SOUND TOGGLE ──
  soundToggle.addEventListener('click', () => {
    state.soundEnabled = !state.soundEnabled;
    if (state.soundEnabled) initAudio();
    soundToggle.textContent = state.soundEnabled ? '🔊' : '🔇';
    soundToggle.classList.toggle('active', state.soundEnabled);
  });

  // ── INIT ──
  input.focus();
  updatePrompt();
  print('Welcome to the terminal blog. Type \u001b[32mhelp\u001b[0m to get started.', 'success');
  print('', '');
})();
