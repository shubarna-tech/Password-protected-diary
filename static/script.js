document.addEventListener('DOMContentLoaded', function () {
    const newPassword = document.querySelector('input[name="new"]');
    const strengthBar = document.createElement('div');
    strengthBar.style.marginTop = '10px';
    newPassword.parentNode.insertBefore(strengthBar, newPassword.nextSibling);

    newPassword.addEventListener('input', () => {
        const val = newPassword.value;
        let strength = 0;
        if (val.length > 5) strength++;
        if (/[A-Z]/.test(val)) strength++;
        if (/[a-z]/.test(val)) strength++;
        if (/\d/.test(val)) strength++;
        if (/[^A-Za-z0-9]/.test(val)) strength++;

        strengthBar.innerHTML = `Password Strength: ${["Very Weak", "Weak", "Fair", "Good", "Strong"][strength - 1] || "Very Weak"}`;
        strengthBar.style.color = ['red', 'orange', 'goldenrod', 'blue', 'green'][strength - 1] || 'red';
    });
});

if (document.getElementById('editor')) {
    const quill = new Quill('#editor', {
        theme: 'snow'
    });

    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function () {
            const hiddenInput = document.getElementById('hidden-text');
            hiddenInput.value = quill.root.innerHTML;
        });
    }
}
if (document.getElementById('calendar')) {
    flatpickr("#calendar", {
        dateFormat: "Y-m-d",
        allowInput: true
    });
}

  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('dark-toggle');
    const enabled = localStorage.getItem('dark-mode') === 'enabled';
    document.body.classList.toggle('dark-mode', enabled);
    toggle.checked = enabled;
    toggle.addEventListener('change', () => {
      const on = toggle.checked;
      document.body.classList.toggle('dark-mode', on);
      localStorage.setItem('dark-mode', on ? 'enabled' : 'disabled');
    });
  });