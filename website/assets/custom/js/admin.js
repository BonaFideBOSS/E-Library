$('#aside-collapse').on('click', function () {
  $('#admin-body aside').toggleClass('collapsed')
  const timeout = $('#admin-body aside').hasClass('collapsed') ? 250 : 50
  setTimeout(() => { $('#admin-body aside .nav-link').toggleClass('text-start') }, timeout);
})