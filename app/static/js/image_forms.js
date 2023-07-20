//$(document).ready(function() {
//    var fieldIndex = getLastTrackImageIndex();
//
//    // Обработчик клика на кнопку "Добавить поле"
//    $('.add-field-btn').click(function() {
//        var field = '<div class="form-group row mb-3 align-items-center field">' +
//                        '<div class="col">' +
//                            '<div class="input-group p-2">' +
//                                '<input type="file" name="track_image_' + fieldIndex + '" class="form-control-file track-image-field">' +
//                                '<button type="button" class="btn btn-danger btn-sm remove-field-btn">' +
//                                    '<i class="fas fa-minus-circle"></i>' +
//                                '</button>' +
//                            '</div>' +
//                        '</div>' +
//                    '</div>';
//
//        $('#fields-container').append(field);
//        fieldIndex++; // Увеличение индекса для следующего поля
//
//        updateFormAttributes(fieldIndex); // Вызов функции updateFormAttributes
//    });
//
//    // Обработчик клика на кнопку "Удалить поле"
//    $(document).on('click', '.remove-field-btn', function() {
//        $(this).closest('.field').remove();
//        updateFormAttributes(); // Вызов функции updateFormAttributes
//    });
//
//    // Функция для обновления атрибутов формы
//    // Функция для обновления атрибутов формы
//    function updateFormAttributes() {
//      var trackImageFields = $('.track-image-field');
//      var existingIndices = [];
//
//      // Собираем индексы существующих полей
//      trackImageFields.each(function() {
//        var fieldName = $(this).attr('name');
//        var index = parseInt(fieldName.split('_')[2]);
//        existingIndices.push(index);
//      });
//
//      // Обновляем имена полей
//      trackImageFields.each(function(index) {
//        var currentIndex = existingIndices.length > 0 ? Math.max.apply(null, existingIndices) + index + 1 : index;
//        var fieldName = 'track_image_' + currentIndex;
//        $(this).attr('name', fieldName); // Обновление имени поля
//      });
//    }
//
//
//    // Функция для получения номера последнего поля с префиксом "track_image_"
//    function getLastTrackImageIndex() {
//        var trackImageFields = $('input[type="file"]').filter(function() {
//                      return this.name.startsWith('track_image_');
//                    });
//        console.log(trackImageFields);
//        var lastIndex = -1;
//        trackImageFields.each(function() {
//            var fieldName = $(this).attr('name');
//            var index = parseInt(fieldName.split('_')[2]);
//            console.log(fieldName);
//            if (index > lastIndex) {
//                lastIndex = index;
//            }
//        });
//        return lastIndex + 1;
//    }
//});


$(document).ready(function() {
  var buffer = []; // Буфер для хранения номеров полей
  initializeBuffer(); // Инициализация буфера при загрузке страницы
  console.log(buffer)

  // Обработчик клика на кнопку "Добавить поле"
  $('.add-field-btn').click(function() {
    var nextIndex = getNextIndex(); // Получение следующего номера из буфера
    var field = '<div class="form-group row mb-3 align-items-center field">' +
                  '<div class="col">' +
                    '<div class="input-group p-2">' +
                      '<input type="file" name="track_image_' + nextIndex + '" class="form-control-file track-image-field">' +
                      '<button type="button" class="btn btn-danger btn-sm remove-field-btn">' +
                        '<i class="fas fa-minus-circle"></i>' +
                      '</button>' +
                    '</div>' +
                  '</div>' +
                '</div>';
    $('#fields-container').append(field);
    updateFormAttributes(); // Вызов функции updateFormAttributes
  });

  // Обработчик клика на кнопку "Удалить поле"
  $(document).on('click', '.remove-field-btn', function() {
    $(this).closest('.field').remove();
    updateFormAttributes(); // Вызов функции updateFormAttributes
  });

  // Функция для обновления атрибутов формы
  function updateFormAttributes() {
    var trackImageFields = $('input[type="file"][name^="track_image_"]');
    trackImageFields.each(function(index) {
      var fieldName = 'track_image_' + buffer[index];
      $(this).attr('name', fieldName); // Обновление имени поля
    });
  }

  // Функция для инициализации буфера
  function initializeBuffer() {
      var trackImageFields = $('input[type="file"][name^="track_image_"]');
      trackImageFields.each(function() {
        var fieldName = $(this).attr('name');
        var index = parseInt(fieldName.split('_')[2]);
        buffer.push(index); // Добавление номеров полей в буфер
      });
    }

  // Функция для получения следующего номера из буфера
  function getNextIndex() {
    var lastIndex = buffer.length > 0 ? buffer[buffer.length - 1] : -1;
    var nextIndex = lastIndex + 1;
    buffer.push(nextIndex); // Добавление следующего номера в буфер
    return nextIndex;
  }
});

