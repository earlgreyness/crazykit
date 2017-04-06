
/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 *  ЛОГИКА
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

(function() {

  // Объект с выбранными призами
  var selectedPrizes = {};

  // Блок с количеством призов в всплывающем окне
  var $tipAmountBox = $('.tip__amount');

  // Список выбранных призов в правилах
  var $prizeList = $('#prize-list');

  // Скрытый input через который передается список выбранных призов
  var $formPrizesList = $('#form-prizes');

  var AMOUNT = 9;


  // Обработка клика по кнопке "Учавствовать"
  $('.prizes-item__btn').click(function() {

    var $prizeItemBtn = $(this);
    var prizeId = +$prizeItemBtn.data('id');
    var prizeName = $prizeItemBtn.closest('.prizes-item').find('.prizes-item__title').text();


    //
    // ВЫБРАНО AMOUNT ПРИЗОВ
    //
    if ($prizeItemBtn.hasClass('off')) {

      return true;

    //
    // ОТМЕНА ВЫБОРА
    //
    } else if ($prizeItemBtn.hasClass('checked')) {

      // Удаляем выбранный приз из объекта
      delete selectedPrizes[prizeId];

      // Возвращаем исходное состояние кнопки
      $prizeItemBtn.removeClass('checked').text('Выбрать');

      // Проверяем нужно ли включить кнопки, выключенные ранее
      if ( Object.keys(selectedPrizes).length === AMOUNT-1) {

        $('.prizes-item__btn.off').removeClass('off');

      }

      // Убираем всплывающее окно, если отменены все призы
      // Убираем галочку с первого пункта правил
      if ( Object.keys(selectedPrizes).length === 0) {

        $('.tip').removeClass('active').removeClass('stop');

        $('#rule-1').removeClass('checked');

      }

      // Удаляем название приза из правил
      $('.prize-name-' + prizeId).remove();

      // Изменяем кол-во в всплывающем окне
      updateTip(AMOUNT - Object.keys(selectedPrizes).length);

    //
    // ВЫБОР
    //
    } else {

      // Добавляем выбранный приз в объект
      selectedPrizes[prizeId] = prizeId;

      // Изменяем кнопку
      $prizeItemBtn.addClass('checked').text('Отменить выбор');

      // Отключаем оставшиеся кнопки, если выбрано AMOUNT призов
      if ( Object.keys(selectedPrizes).length === AMOUNT) {

        $('.prizes-item__btn').not('.checked').addClass('off');

      }

      // Показываем всплывающее окно, если выбран первый товар
      // Ставим галочку у первого пункта правил
      if ( Object.keys(selectedPrizes).length === 1) {

        var tip = $('.tip');

        var tipOffsetTop = tip.offset().top;
        var profileOffsetTop = $('#profile').offset().top;

        if ((tipOffsetTop + 70) < profileOffsetTop) {

          tip.addClass('active');

        } else {

          tip.addClass('stop').addClass('active');

        }

        $('#rule-1').addClass('checked');

      }

      // Добавляем название приза в правила
      $prizeList.append('<li class="prize-name-' + prizeId + '">' + prizeName + '</li>');

      // Изменяем кол-во в всплывающем окне
      updateTip(AMOUNT - Object.keys(selectedPrizes).length);

    }

  });

  // Обновляет кол-во призов в всплывающем окне
  function updateTip(value) {

    if (value === 0) {

      $tipAmountBox.text(value + ' призов');

    } else if (value === 1) {

      $tipAmountBox.text(value + ' приз');

    } else if (value === 5) {

      $tipAmountBox.text(value + ' призов');

      } else if (value === 6) {

      $tipAmountBox.text(value + ' призов');

      } else if (value === 7) {

      $tipAmountBox.text(value + ' призов');

     } else if (value === 8) {

      $tipAmountBox.text(value + ' призов');



    } else {

      $tipAmountBox.text(value + ' приза');

    }

  }


  //
  // Останавливает всплывающее окно над "Анкетой"
  //
  $(window).scroll(function() {

    var tip = $('.tip');

    var tipOffsetTop = tip.offset().top;
    var profileOffsetTop = $('#profile').offset().top;

    if ((tipOffsetTop + 70) >= profileOffsetTop && tip.hasClass('active')) {

      tip.addClass('stop');

    }

    if (profileOffsetTop - (window.pageYOffset + document.documentElement.clientHeight) > 0) {

      tip.removeClass('stop');

    }

  });


  //
  // Обработка формы
  //
  $('#form').submit(function() {

    var form = $(this);


    if (Object.keys(selectedPrizes).length === 0) {

      $('.form-choose').show(0);

      setTimeout(function() {
        $('.form-choose').hide(0);
      }, 10000);

      return false;


    // Если есть незаполненные поля подсвечиваем их
    } else if (hasBlankRequiredFields(form)) {

      return false;


    // Если все ОК – отправляем форму на сервер Ajax'ом
    } else {

      // Собираем список призов
      var resultIdsString = '';

      for (var id in selectedPrizes) {
        resultIdsString += selectedPrizes[id] + ';';
      }

      // Добавляем список в скрытый input (name="prizes")
      $formPrizesList.val(resultIdsString);

      // Отправка формы
      $.ajax({

        url: form.attr('action'),
        type: form.attr('method'),
        data: form.serialize(),

        success: function() {

          // Скрываем фон и форму
          $('.form, .form__wrapper').addClass('hidden');

          // Скрываем всплывающее окно
          $('.tip').hide();

          // Отключаем все кнопки призов
          $('.prizes-item__btn').removeClass('active').addClass('off');

          // Показываем заглушку
          $('.form-success').addClass('active');

          // Отмечаем вторую галочку
          $('#rule-2').addClass('checked');

          // Отмечаем третью галочку через 10 сек
          setTimeout(function() {

            $('#rule-3').addClass('checked');

          }, 10000);

          // Отмечаем четвертую галочку через 10 сек
          setTimeout(function() {

            $('#rule-4').addClass('checked');

          }, 15000);

        },

        error: function() {

          alert('Что-то пошло не так. Попробуйте снова!');

        }

      });

      return false;

    }

  });

})();



/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 *  МОБИЛЬНОЕ МЕНЮ
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

$('#hamburger').click(function() {

  var mobileMenu = $('.header-menu');

  if (mobileMenu.is(':visible')) {

    mobileMenu.hide();

  } else {

    mobileMenu.show();

  }

});



/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 *  Плавная прокрутка до якоря
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

(function() {

  var viewportWidth = document.documentElement.clientWidth;

  if ( viewportWidth >= 1024 ) {

    $('body').on('click', 'a[href^="#"]', function(event) {

      if ( this.hash === '#details' || this.hash === '#gifts' ) {

        $('html, body').stop().animate({

          scrollTop: $(this.hash).offset().top + 70

        }, 700);

      } else if ( this.hash === '#profile' ) {

        $('html, body').stop().animate({

          scrollTop: $(this.hash).offset().top

        }, 500);

      } else {

        $('html, body').stop().animate({

          scrollTop: $(this.hash).offset().top - 50

        }, 500);

      }

      event.preventDefault();

    } );

  }

})();



/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 *  Колонки одинаковой высоты у плиток
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

$('.gifts-item__textual').matchHeight();

$('.prizes-item__textual').matchHeight();

$(window).on('resize', function() {

  $('.gifts-item__textual').matchHeight();

  $('.prizes-item__textual').matchHeight();

});



/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 *  Форма
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */


//
// Кастомный select
//
$('select').selectize().on('change', function(value) {

  if (value !== 'Не выбрано') {

    $(this).find(' + .selectize-control .item').css('color', '#2c2c2c');

  } else {

    $(this).find(' + .selectize-control .item').css('color', '#bcbcbc');

  }

});

// Отключение возможности ввода в select'е
$('.selectize-input input').prop('disabled', true);




/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 *
 *  Вспомогательные функции
 *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

//
// Обязательные поля
//
function hasBlankRequiredFields( form ) {
  var error = false;

  form.find( 'input, select' ).each(function() {
    var input = $( this );

    if ( input.data( 'required' ) && input.val() === '' ) {

      input.addClass( 'required' );

      input.on( 'blur', function() {

        if ( $( this ).val() !== '' ) {
          $( this ).removeClass( 'required' );
        }

      });

      error = true;

    } else if (input.val() === 'Не выбрано') {

      input.addClass('required');

      input.on( 'change', function() {

        if ( $( this ).val() !== 'Не выбрано' ) {
          $( this ).removeClass( 'required' );
        }

      });

      error = true;

    } else if ( input.attr('type') === 'checkbox' && input.data( 'required' ) && !input.prop('checked') ) {

      input.addClass( 'required' );

      input.on( 'blur', function() {

        if ( $( this ).val() !== '' ) {
          $( this ).removeClass( 'required' );
        }

      });

    }
  });

  if ( error ) {
    form
      .find( '.required' )
      .first()
      .focus();
  }

  return error;
}


$(document).ready(function () {

  // jQuery Inputmask
  $('#form-tel').inputmask({
    mask: '8 (999) 999-99-99[9999]',
    greedy: false,
    // clearIncomplete: true,
  });

})
