$(document).ready(function () {
  rotate_nav_books()
})

function rotate_nav_books() {
  const nav = document.querySelectorAll('.nav-books')
  nav.forEach(nav_item => {
    const types = Array.from(nav_item.querySelectorAll('li'))
    var index = 1;
    setInterval(() => {
      $(types).removeClass('active')
      $(types[index]).addClass('active')
      index = (index + 1) % types.length
    }, 2000);
  })
}