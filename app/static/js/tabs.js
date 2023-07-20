function checkCustomValue(select) {
  var customValueInput = select.nextElementSibling;
  if (select.value === '') {
    customValueInput.style.display = 'block';
  } else {
    customValueInput.style.display = 'none';
  }
}