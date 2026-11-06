/* Touch, mouse and keyboard all use the same click action. No hover state. */
(() => {
  const floor = document.querySelector('.store-floor');
  if (!floor) return;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  for (const trigger of floor.querySelectorAll('[data-store-object]')) {
    const fixture = document.getElementById(`fixture-${trigger.dataset.storeObject}`);
    const dialog = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!fixture) continue;
    if (dialog && typeof dialog.showModal !== 'function') continue;
    trigger.hidden = false;
    trigger.addEventListener('focus', () => {
      if (trigger.matches(':focus-visible')) fixture.classList.add('is-focused');
    });
    trigger.addEventListener('blur', () => fixture.classList.remove('is-focused'));
    let feedbackTimer;
    trigger.addEventListener('click', event => {
      // Preserve modified clicks, open-in-new-tab, downloads and browser history.
      if (trigger.tagName === 'A' && (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0)) return;
      if (trigger.tagName === 'A') event.preventDefault();
      clearTimeout(feedbackTimer);
      fixture.classList.remove('is-active');
      // Restart only this small, finite object animation.
      void fixture.getBoundingClientRect();
      fixture.classList.add('is-active');
      feedbackTimer = setTimeout(() => fixture.classList.remove('is-active'), 360);
      if (dialog) {
        if (dialog.open) dialog.close();
        else dialog.showModal();
      } else {
        setTimeout(() => window.location.assign(trigger.href), reducedMotion.matches ? 0 : 220);
      }
    });
    if (!dialog) continue;
    // Click the surrounding store to put the label back. Dragging from inside
    // the paper never accidentally closes it.
    let outsideDown = false;
    const outside = event => {
      const rect = dialog.getBoundingClientRect();
      return event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom);
    };
    dialog.addEventListener('pointerdown', event => { outsideDown = outside(event); });
    dialog.addEventListener('click', event => {
      if (outsideDown && outside(event)) dialog.close();
      outsideDown = false;
    });
    dialog.addEventListener('close', () => {
      fixture.classList.remove('is-active');
      trigger.focus({preventScroll:true});
    });
  }
})();
