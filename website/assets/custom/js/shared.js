// Clear previous requests
if (window.history.replaceState) {
  window.history.replaceState(null, null, window.location.href);
}


// Initialize AJAX headers with CSRF token
const csrf_token = document.querySelector('meta[name="csrf_token"]').getAttribute('content')
$.ajaxSetup({ headers: { 'X-CSRFToken': csrf_token } });

// Tooltips
function enable_tooltips() {
  const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
  const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
}
enable_tooltips()


// Notification Toast
function notify(message, delay = 10) {
  delay = delay * 1000
  toast_container = document.getElementById("notification-toast");
  const wrapper = document.createElement("div");
  wrapper.classList.add("toast", 'fade-in-right', 'bg-custom-gradient', "border-0", "shadow-lg", 'rounded-3');
  wrapper.setAttribute("data-bs-delay", delay);
  const website_name = document.querySelector('meta[property="og:title"]').getAttribute('content')
  const website_logo = '/assets/img/logo-bg-light.png'
  wrapper.innerHTML =
    `<div class="toast-header border-0 rounded-top-3">
      <img src="${website_logo}" width="20" class="me-2">
      <strong class="me-auto">${website_name}</strong>
      <small>Just Now</small>
      <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
    </div>
    <div class="toast-body fs-6 text-light">${message}</div>`;
  toast_container.append(wrapper);
  const toast = new bootstrap.Toast(wrapper);
  toast.show();
}


// Disable submit button on form submission
$('form').on('submit', function () {
  const loader = `<div class="d-flex justify-content-center align-items-center gap-2">
      <span class="spinner-grow spinner-grow-sm opacity-50"></span>
      <span role="status">Loading...</span>
    </div>`
  const btn = $(this).find('button[type="submit"]')
  if (this.checkValidity()) {
    $(btn).attr('disabled', true)
    if ($(btn).attr('data-show-loader') != 'false') { $(btn).html(loader) }
  }
})


// Scroll-To-Top button function
const scroll_to_top = document.getElementById("scroll-to-top");
window.onscroll = () => {
  if (document.body.scrollTop > 500 || document.documentElement.scrollTop > 500) {
    scroll_to_top.classList.add('show')
    scroll_to_top.classList.remove('hide')
  } else {
    scroll_to_top.classList.add('hide')
    scroll_to_top.classList.remove('show')
  }
}
$(scroll_to_top).on('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); })


// Function to resend email verification mail
$('.resend-otp').on('click', function (e) {
  e.preventDefault()
  $.post($(this).data('url'))
  notify('Email sent!')
})

function previewFile(fileInput, img_class) {
  for (const file of fileInput.files) {
    const reader = new FileReader();
    reader.onload = function (e) {
      if (file.type.startsWith('image/')) { $(`.${img_class}`).attr('src', e.target.result) }
    };
    reader.readAsDataURL(file);
  }
}

$('input[type="file"]').on('change', function () {
  if ($(this).data('show-preview')) {
    previewFile(this, $(this).data('preview-class'))
  }
})