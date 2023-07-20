var images = document.querySelectorAll('img');

for (var i = 0; i < images.length; i++) {

  images[i].addEventListener('click', function() {

    if (this.src.includes('logo.jpg')) {
      return;
    }

    var modal = document.createElement('div');
    modal.classList.add('mymodal');


    var modalImage = document.createElement('img');
    modalImage.src = this.src;

    modal.appendChild(modalImage);

    document.body.appendChild(modal);

    // Добавляем обработчик события на клик по модальному окну
    modal.addEventListener('click', function() {
      // Удаляем модальное окно
      document.body.removeChild(modal);
    });
  });
}
