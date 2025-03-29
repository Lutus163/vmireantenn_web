document.addEventListener('DOMContentLoaded', function() {
    // Получаем все карточки товаров
    let cards = document.querySelectorAll('.card');

    cards.forEach(function(card) {
        // Получаем изображение в карточке
        let image = card.querySelector('.card-img-top');
        // Получаем название товара
        let title = card.querySelector('.card-title');
        // Получаем текст описания товара
        let text = card.querySelector('.card-text');

        // Делаем изображение по центру
        image.classList.add('mx-auto');
        // Делаем название товара по центру
        title.classList.add('text-center');
        // Делаем текст описания товара по центру
        text.classList.add('text-center');
    });
});
