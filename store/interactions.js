/* Tap/click/keyboard only. Labels are tiny non-modal notes beside real objects. */
(() => {
  const floor = document.querySelector('.store-floor');
  if (!floor) return;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const choice = new URLSearchParams(location.search).get('motion');
  let motionOverride = choice === 'on';
  try {
    if (choice === 'on') sessionStorage.setItem('57store-motion', 'on');
    if (choice === 'off') sessionStorage.removeItem('57store-motion');
    motionOverride = sessionStorage.getItem('57store-motion') === 'on';
  } catch { /* The query still works if session storage is unavailable. */ }
  document.documentElement.classList.toggle('motion-enabled', motionOverride);
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
  // Don't animate fixtures that are out of view, or an inactive browser tab.
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) entry.target.classList.toggle('is-away', !entry.isIntersecting);
    }, {rootMargin:'80px'});
    floor.querySelectorAll('svg > g[id^="fixture-"]').forEach(node => observer.observe(node));
  }
  const pause = () => document.documentElement.classList.toggle('store-paused', document.hidden);
  document.addEventListener('visibilitychange', pause);
  pause();
})();
