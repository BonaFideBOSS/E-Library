$(document).ready(function () {
  get_books('book', 'view_count', '#most-read-books')
  get_books('book', 'download_count', '#most-downloaded-books')
  get_books('video', 'view_count', '#most-watched-videos')
  get_categories()
})

function get_books(book_type, sort, container) {
  const url = '/home-books-api'
  const data = { 'book_type': book_type, 'sort': sort }
  get_api_data(url, data, container)
}

function get_categories() {
  const url = '/home-categories-api'
  get_api_data(url, {}, '#featured-categories')
}

function get_api_data(url, data, container) {
  $.post(url, data).done(function (response) { $(container).html(response) })
}