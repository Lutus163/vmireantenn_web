const backToTopBtn = document.querySelector('.back-to-top');

// Проверяем ширину экрана при загрузке
const isMobile = window.matchMedia('(max-width: 767px)').matches;

if (isMobile) {
  // Показываем или скрываем кнопку при прокрутке, только если это мобильное устройство
  window.addEventListener('scroll', () => {
    if (window.scrollY > 200) {
      backToTopBtn.style.display = 'block';
    } else {
      backToTopBtn.style.display = 'none';
    }
  });

  // Обработка клика на кнопку
  backToTopBtn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });

    // Убираем фокус с кнопки после нажатия
    if (document.activeElement === backToTopBtn) {
      backToTopBtn.blur();
    }
  });

  // Обработка события touchend на мобильных устройствах
  backToTopBtn.addEventListener('touchend', () => {
    // Убираем фокус с кнопки после нажатия
    if (document.activeElement === backToTopBtn) {
      backToTopBtn.blur();
    }
  });
}
