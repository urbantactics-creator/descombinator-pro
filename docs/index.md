<style>
/* Fixed top navigation - clean style */
.topnav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #fff;
  color: #000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  z-index: 1000;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border-bottom: 1px solid #eaeaea;
}

.topnav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.topnav > ul > li {
  position: relative;
  flex: 1 1 auto;
}

.topnav > ul > li > a {
  display: block;
  padding: 1em 1.2em;
  color: #000;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95em;
  letter-spacing: 0.01em;
  border-right: none;
  transition: background 0.2s, color 0.2s;
}

.topnav > ul > li > a:hover {
  background: #f5f5f5;
  color: #000;
}

/* Dropdown - clean style */
.topnav .dropdown {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  background: #fff;
  min-width: 220px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  border-bottom: 2px solid #000;
}

.topnav li:hover .dropdown {
  display: block;
}

.topnav .dropdown li {
  flex: 1 1 100%;
}

.topnav .dropdown a {
  padding: 0.8em 1.2em;
  border-bottom: 1px solid #f0f0f0;
  font-size: 0.9em;
  color: #000;
  font-weight: 500;
}

.topnav .dropdown a:hover {
  background: #f5f5f5;
  color: #000;
}

/* Mobile hamburger */
.nav-toggle {
  display: none;
  background: none;
  border: none;
  color: #000;
  font-weight: 700;
  font-size: 1.5em;
  padding: 0.5em 1em;
  cursor: pointer;
}

/* Spacer for fixed nav */
body {
  padding-top: 3em;
}

/* Responsive */
@media (max-width: 768px) {
  .nav-toggle {
    display: block;
  }
  .topnav ul {
    display: none;
    flex-direction: column;
    width: 100%;
  }
  .topnav.open ul {
    display: flex;
  }
  .topnav > ul > li > a {
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
  }
  .topnav .dropdown {
    position: static;
    box-shadow: none;
    border-bottom: 2px solid #000;
    background: #fafafa;
  }
}
</style>

<nav class="topnav" id="topnav">
  <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation">☰</button>
  <ul>
    <li><a href="https://urbantactics-creator.github.io/descombinator-pro/">Home</a></li>
    <li>
      <a href="#">Getting Started ▾</a>
      <ul class="dropdown">
        <li><a href="tutorials/installation.html">Installation</a></li>
        <li><a href="tutorials/quick-start.html">Quick Start</a></li>
        <li><a href="tutorials/feature-walkthrough.html">Feature Walkthrough</a></li>
      </ul>
    </li>
    <li>
      <a href="#">User Guides ▾</a>
      <ul class="dropdown">
        <li><a href="guides/user-guide.html">User Guide</a></li>
        <li><a href="how-to/export-audio.html">Export Audio</a></li>
        <li><a href="how-to/play-mixed-tracks.html">Play Mixed Tracks</a></li>
        <li><a href="how-to/adjust-settings.html">Adjust Settings</a></li>
      </ul>
    </li>
    <li>
      <a href="#">Architecture ▾</a>
      <ul class="dropdown">
        <li><a href="explanations/architecture/overview.html">Overview</a></li>
        <li><a href="architecture/README.html">ADRs Index</a></li>
        <li><a href="architecture/adr-001-modular-monolith.html">ADR-001</a></li>
        <li><a href="architecture/adr-002-async-first.html">ADR-002</a></li>
        <li><a href="architecture/adr-003-pydantic-state.html">ADR-003</a></li>
        <li><a href="architecture/adr-004-service-layer.html">ADR-004</a></li>
        <li><a href="architecture/adr-005-separation-backends.html">ADR-005</a></li>
        <li><a href="architecture/adr-006-benchmark-regression-gate.html">ADR-006</a></li>
        <li><a href="architecture/dependency-graph.html">Dependency Graph</a></li>
        <li><a href="architecture/module-contracts.html">Module Contracts</a></li>
      </ul>
    </li>
    <li>
      <a href="#">Explanations ▾</a>
      <ul class="dropdown">
        <li><a href="explanations/tech-stack.html">Tech Stack</a></li>
        <li><a href="explanations/architecture/separation-engine.html">Separation Engine</a></li>
        <li><a href="explanations/architecture/performance-optimization.html">Performance</a></li>
        <li><a href="explanations/design-decisions/async-first-adr.html">Async-First</a></li>
        <li><a href="explanations/design-decisions/modular-monolith-adr.html">Modular Monolith</a></li>
      </ul>
    </li>
    <li>
      <a href="#">API ▾</a>
      <ul class="dropdown">
        <li><a href="api/README.html">API Overview</a></li>
        <li><a href="api/python.html">Python API</a></li>
        <li><a href="api/guides.html">API Guides</a></li>
      </ul>
    </li>
    <li>
      <a href="#">Development ▾</a>
      <ul class="dropdown">
        <li><a href="development/development.html">Development Guide</a></li>
        <li><a href="development/performance.html">Performance Guide</a></li>
        <li><a href="development/performance/tuning.html">Performance Tuning</a></li>
      </ul>
    </li>
    <li><a href="faq.html">FAQ</a></li>
    <li><a href="troubleshooting/troubleshooting.html">Troubleshooting</a></li>
    <li><a href="license-compliance/license-compliance.html">License</a></li>
    <li><a href="technical-debt/mypy-strict-coverage.html">Technical Debt</a></li>
    <li><a href="changelog.html">Changelog</a></li>
  </ul>
</nav>

<script>
document.getElementById('navToggle').addEventListener('click', function() {
  document.getElementById('topnav').classList.toggle('open');
});
</script>

# Descombinator Pro

Separate any song into vocals and instrumental tracks locally — fast, free, private.
No internet required, no file uploads. Studio-quality results in seconds.

## What is Descombinator Pro?

Descombinator Pro is a desktop application that uses AI to separate audio tracks into **vocals** and **instrumental** stems. All processing happens on your machine — your files never leave your computer.

## Key Features

- **High-quality separation** powered by Demucs (htdemucs_ft, mdx_extra) and Open-Unmix (umxhq)
- **Modern, minimal UI** built with PySide6 — dark/light theme support
- **Fast local processing** with PyTorch acceleration
- **On-device privacy** — no files uploaded to the internet
- **Synchronized multi-track playback** with per-track volume/mute, seek, and gapless mixing
- **Waveform visualization** with playback position tracking
- **Multi-format export** — WAV, FLAC, MP3, M4A with metadata embedding
- **Performance-tested** — 16 benchmark gates enforced in CI
- **Thermal monitoring** — cross-platform CPU/GPU temperature sampling
- **Cross-platform** support (Linux, macOS, Windows)

## Who is this for?

- 🎵 **Musicians** wanting stems for remixing
- 🎬 **Content creators** needing clean instrumentals
- 🎛️ **Producers** needing high-quality stems
