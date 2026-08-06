// Replace this with your deployed Google Apps Script Web App URL
const APPS_SCRIPT_URL = 'REPLACE_ME';

const form = document.getElementById('signupForm');
const successMessage = document.getElementById('successMessage');
const errorMessage = document.getElementById('errorMessage');
const errorDetail = document.getElementById('errorDetail');

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  // Clear previous messages
  successMessage.style.display = 'none';
  errorMessage.style.display = 'none';
  errorDetail.textContent = '';

  // Validate that APPS_SCRIPT_URL has been set
  if (APPS_SCRIPT_URL === 'REPLACE_ME') {
    errorDetail.textContent = 'Configuration error: Apps Script URL not set.';
    errorMessage.style.display = 'block';
    return;
  }

  // Gather form data
  const formData = new FormData(form);
  const data = {
    parent_email: formData.get('parent_email'),
    child_name: formData.get('child_name'),
    desired_time: formData.get('desired_time'),
    timezone: formData.get('timezone'),
    website: formData.get('website') // Honeypot
  };

  try {
    // POST to Apps Script with text/plain to skip CORS preflight
    const response = await fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'text/plain;charset=utf-8'
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (result.status === 'ok') {
      successMessage.style.display = 'block';
      form.reset();
      document.getElementById('timezone').value = 'America/Denver';
      document.getElementById('desired_time').value = '18:30';
    } else {
      const errors = result.errors || ['Unknown error'];
      errorDetail.textContent = errors.join(', ');
      errorMessage.style.display = 'block';
    }
  } catch (error) {
    errorDetail.textContent = `Network error: ${error.message}`;
    errorMessage.style.display = 'block';
  }
});
