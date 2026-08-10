<style>
/* Hide default theme h1 title */
.site-header h1 {
  font-size: 0;
  height: 0;
  margin: 0;
  padding: 0;
  overflow: hidden;
}
.site-header h1 a {
  display: block;
  width: 359px;
  height: 63px;
  background: url('assets/icons/LOGO-HZ.svg') no-repeat;
  text-indent: -9999px;
  overflow: hidden;
}
.site-header p {
  clear: both;
  margin-top: 1em;
}
.docs-nav {
  margin: 2em 0;
}
.docs-nav h2 {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-size: 1.2em;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 0.3em;
}
.docs-nav ul {
  list-style: none;
  padding-left: 0;
  margin: 0.5em 0;
}
.docs-nav li {
  margin: 0.4em 0;
}
.docs-nav a {
  text-decoration: none;
}
.docs-nav a:hover {
  text-decoration: underline;
}
</style>

<p><a href="https://urbantactics-creator.github.io/descombinator-pro/tutorials/feature-walkthrough.html#:~:text=Descombinator%20Pro">
  <img src="assets/icons/LOGO-HZ.svg" alt="Descombinator Pro" style="max-width: 359px; height: auto; display: block;">
</a></p>

<p>Separate any song into vocals and instrumental tracks locally — fast, free, private.
No internet required, no file uploads. Studio-quality results in seconds.</p>

<div class="docs-nav">

## 📚 Documentation

### Getting Started
- [Installation](tutorials/installation.md)
- [Quick Start](tutorials/quick-start.md)
- [Feature Walkthrough](tutorials/feature-walkthrough.md)

### User Guides
- [User Guide](guides/user-guide.md)
- [How-to: Export Audio](how-to/export-audio.md)
- [How-to: Play Mixed Tracks](how-to/play-mixed-tracks.md)
- [How-to: Adjust Settings](how-to/adjust-settings.md)

### Architecture
- [Architecture Overview](explanations/architecture/overview.md)
- [ADRs Index](architecture/README.md)
- [ADR-001: Modular Monolith](architecture/adr-001-modular-monolith.md)
- [ADR-002: Async-First](architecture/adr-002-async-first.md)
- [ADR-003: Pydantic State](architecture/adr-003-pydantic-state.md)
- [ADR-004: Service Layer](architecture/adr-004-service-layer.md)
- [ADR-005: Separation Backends](architecture/adr-005-separation-backends.md)
- [ADR-006: Benchmark Regression Gate](architecture/adr-006-benchmark-regression-gate.md)
- [Dependency Graph](architecture/dependency-graph.md)
- [Module Contracts](architecture/module-contracts.md)

### Explanations
- [Tech Stack](explanations/tech-stack.md)
- [Separation Engine](explanations/architecture/separation-engine.md)
- [Performance Optimization](explanations/architecture/performance-optimization.md)
- [Design Decisions: Async-First](explanations/design-decisions/async-first-adr.md)
- [Design Decisions: Modular Monolith](explanations/design-decisions/modular-monolith-adr.md)

### API Reference
- [API Overview](api/README.md)
- [Python API](api/python.md)
- [API Guides](api/guides.md)

### Development
- [Development Guide](development/development.md)
- [Performance Guide](development/performance.md)
- [Performance Tuning](development/performance/tuning.md)

### Support
- [FAQ](faq.md)
- [Troubleshooting](troubleshooting/troubleshooting.md)

### Project Info
- [License Compliance](license-compliance/license-compliance.md)
- [Technical Debt: Mypy Strict Coverage](technical-debt/mypy-strict-coverage.md)
- [Changelog](changelog.md)

</div>
<!-- cache-bust: header-css-fix -->
