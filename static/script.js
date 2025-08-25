document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('.input-form');
  const overlay = document.getElementById('loading-overlay');
  if (!form || !overlay) return;
  const sendButton = form.querySelector('button[type="submit"]');
  const messageInput = form.querySelector('input[name="message"]');
  const loadingText = document.getElementById('loading-text');
  const expertCheckbox = document.querySelector('.mode-form input[name="expert_mode"][type="checkbox"]');
  form.addEventListener('submit', () => {
    overlay.classList.remove('hidden');
    if (sendButton) sendButton.disabled = true;
    // Keep the message input enabled during submission so its value is sent
    // Disable it asynchronously once the submission has started
    if (messageInput) {
      setTimeout(() => {
        messageInput.disabled = true;
      }, 0);
    }
    if (loadingText) {
      if (expertCheckbox && expertCheckbox.checked) {
        loadingText.textContent = 'Creating expert prompt...';
        setTimeout(() => {
          loadingText.textContent = 'Generating response...';
        }, 1000);
      } else {
        loadingText.textContent = 'Generating response...';
      }
    }
  });
});
