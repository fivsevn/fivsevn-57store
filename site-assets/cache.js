(() => {
  function connect() {
    document.querySelectorAll('form[data-cache-reveal]').forEach(form => {
      form.addEventListener('submit', event => {
        event.preventDefault();
        const reply = document.getElementById(form.dataset.cacheReveal);
        if (!reply) return;
        reply.hidden = false;
        form.hidden = true;
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', connect, {once: true});
  else connect();
})();
