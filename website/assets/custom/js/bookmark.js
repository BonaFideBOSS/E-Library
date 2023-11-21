$('.bookmark').on('click', function () {
  $(this).attr('disabled', true)
  const btn = $(this)
  const icon = $(this).html()
  $(this).html('<i class="fa-sharp fa-regular fa-circle-dashed fa-spin"></i>')

  const book_id = $(this).data('book-id')
  const action = $(this).hasClass('btn-success') ? 'remove' : 'add'
  const data = { "book_id": book_id, "action": action }
  const url = '/user/manage-bookmark'

  $.post(url, data)
    .done(function (response) {
      if (response.success) {
        $(btn).toggleClass('btn-dark')
        $(btn).toggleClass('btn-success')
        $(btn).html('<i class="fa-sharp fa-regular fa-check"></i>')
      }
    })
    .fail(function () { notify('Failed to perform action.') })
    .always(function () { setTimeout(() => { $(btn).attr('disabled', false); $(btn).html(icon) }, 5000); })
})