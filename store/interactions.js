/* Tap/click/keyboard only. Labels are tiny non-modal notes beside real objects. */
(() => {
  const floor = document.querySelector('.store-floor');
  if (!floor) return;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const choice = new URLSearchParams(location.search).get('motion');
  // A deliberate choice follows the visitor across preview tabs and return
  // links. System reduced motion remains the default until that choice exists.
  const motionKey = '57store-motion';
  let savedChoice = null;
  try { savedChoice = localStorage.getItem(motionKey); } catch { /* Storage is optional. */ }
  // Preserve an explicit choice made by the earlier per-tab preview.
  if (!savedChoice) {
    try { savedChoice = sessionStorage.getItem(motionKey); } catch { /* No storage access. */ }
  }
  let motionOverride = choice === 'on' || (choice !== 'off' && savedChoice === 'on');
  for (const storageName of ['localStorage', 'sessionStorage']) {
    try {
      if (choice === 'off') window[storageName].removeItem(motionKey);
      else if (motionOverride) window[storageName].setItem(motionKey, 'on');
    } catch { /* The explicit query works even when storage is blocked. */ }
  }
  const syncMotion = () => document.documentElement.classList.toggle('motion-enabled', motionOverride);
  syncMotion();
  const motionAllowed = () => motionOverride || !reducedMotion.matches;
  let openLabel = null;
  let openTrigger = null;
  const close = () => {
    if (openLabel) openLabel.hidden = true;
    if (openTrigger) openTrigger.setAttribute('aria-expanded', 'false');
    openLabel = openTrigger = null;
  };
  const position = () => {
    if (!openLabel || !openTrigger) return;
    const room = floor.getBoundingClientRect();
    const target = openTrigger.getBoundingClientRect();
    const label = openLabel.getBoundingClientRect();
    const left = Math.max(8, Math.min(room.width - label.width - 8, target.left - room.left + target.width / 2 - label.width / 2));
    const above = target.top - room.top - label.height - 8;
    const top = target.top - label.height - 8 > 8 ? above : target.bottom - room.top + 8;
    openLabel.style.left = `${left}px`;
    openLabel.style.top = `${Math.max(8, Math.min(room.height-label.height-8, top))}px`;
  };
  for (const trigger of floor.querySelectorAll('[data-store-object]')) {
    const fixture = document.getElementById(`fixture-${trigger.dataset.storeObject}`);
    const label = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!fixture) continue;
    trigger.hidden = false;
    trigger.addEventListener('focus', () => {
      if (trigger.matches(':focus-visible')) fixture.classList.add('is-focused');
    });
    trigger.addEventListener('blur', () => fixture.classList.remove('is-focused'));
    let timer;
    trigger.addEventListener('click', event => {
      if (trigger.tagName === 'A' && (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0)) return;
      if (trigger.tagName === 'A') event.preventDefault();
      const wasOpen = openTrigger === trigger;
      close();
      clearTimeout(timer);
      fixture.classList.remove('is-active');
      void fixture.getBoundingClientRect();
      fixture.classList.add('is-active');
      timer = setTimeout(() => fixture.classList.remove('is-active'), 450);
      if (label && !wasOpen) {
        openLabel = label; openTrigger = trigger;
        trigger.setAttribute('aria-expanded', 'true');
        label.hidden = false; position();
      } else if (!label) {
        setTimeout(() => location.assign(trigger.href), motionAllowed() ? 240 : 0);
      }
    });
  }
  document.addEventListener('click', event => {
    if (!event.target.closest('[data-store-object]')) close();
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') close();
  });
  addEventListener('resize', position);
  // Observe stable HTML touch surfaces. SVG-group intersection reporting can
  // vary in embedded webviews and animated geometry must not decide its own
  // visibility. Decorative groups without a control remain inexpensive CSS.
  const observed = new Map();
  for (const trigger of floor.querySelectorAll('[data-store-object]')) {
    const fixture = document.getElementById(`fixture-${trigger.dataset.storeObject}`);
    if (fixture) observed.set(trigger, fixture);
  }
  const canObserve = 'IntersectionObserver' in window;
  const syncVisibility = () => {
    const height = window.innerHeight;
    const width = window.innerWidth;
    for (const [trigger, fixture] of observed) {
      const box = trigger.getBoundingClientRect();
      fixture.classList.toggle('is-away', canObserve && (box.bottom < -80 || box.top > height + 80 || box.right < 0 || box.left > width));
    }
    document.documentElement.classList.toggle('store-paused', document.hidden);
  };
  if (canObserve) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) observed.get(entry.target)?.classList.toggle('is-away', !entry.isIntersecting);
    }, {rootMargin:'80px'});
    for (const trigger of observed.keys()) observer.observe(trigger);
  }
  // Back/forward-cache restores and embedded-tab activation can preserve old
  // pause classes; reconcile geometry and visibility when the surface returns.
  const resume = () => { syncMotion(); syncVisibility(); };
  document.addEventListener('visibilitychange', syncVisibility);
  addEventListener('pageshow', resume);
  addEventListener('focus', resume);
  addEventListener('resize', syncVisibility);
  addEventListener('storage', event => {
    if (event.key !== motionKey) return;
    motionOverride = event.newValue === 'on';
    try {
      if (motionOverride) sessionStorage.setItem(motionKey, 'on');
      else sessionStorage.removeItem(motionKey);
    } catch { /* Cross-tab preference still updates without session storage. */ }
    resume();
  });
  resume();
})();
