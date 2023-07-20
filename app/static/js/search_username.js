const filterInput = document.getElementById('filter-input');
const rows = document.querySelectorAll('tbody tr');

filterInput.addEventListener('input', function() {
const filterValue = this.value.toLowerCase();
rows.forEach(row => {
  const nickname = row.querySelector('td:first-child a').textContent.toLowerCase();
  if (nickname.startsWith(filterValue)) {
    row.style.display = '';
  } else {
    row.style.display = 'none';
  }
});
});