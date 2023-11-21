var all_loaded = 0

$(document).ready(function () {
  get_books('book', 'view_count', '#most-read-books')
  get_books('book', 'download_count', '#most-downloaded-books')
  get_books('video', 'view_count', '#most-watched-videos')
  get_categories()
})

async function get_books(book_type, sort, container) {
  const url = '/home-books-api'
  const data = { 'book_type': book_type, 'sort': sort }
  await get_api_data(url, data, container)
  all_loaded++
  if (all_loaded == 3 && is_user_logged_in) { bookmark() }
}

function get_categories() {
  const url = '/home-categories-api'
  get_api_data(url, {}, '#featured-categories')
}

async function get_api_data(url, data, container) {
  await $.post(url, data).done(function (response) { $(container).html(response) })
}