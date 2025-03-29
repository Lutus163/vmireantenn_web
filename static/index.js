let tg = window.Telegram.WebApp;



tg.expand();

tg.MainButton.textColor = '#FFFFFF';
tg.MainButton.color = '#2cab37';
let a = document.getElementById("total");



const amount_items_url='/amount_items';
const add_to_cart_url='/add_to_cart/';
const amount_items_cart_url='/amount_items_cart';
const cart_total_url='/cart_total';
let amount_items = 0
let price = 0

fetch(cart_total_url,
{
  method: 'POST',
})
    .then((response) => {
        return response.json();
    })
    .then((myjson) => {
    price = Number(myjson.total);
    if(price == 0) {
    a.style.visibility = 'hidden';

    } else {
    tg.MainButton.setText("Итого: "+ String(price) + " В корзину?");
    a.innerHTML = "Итого: " + String(price)  + " В корзину?";
    }
    });



fetch(amount_items_url)
    .then(data => data.json())
    .then(response =>  {

      amount_items = Number(response.amount);
      let buttons = new Array(amount_items);
      let items_price = new Array(amount_items);



for(let i = 0; i < buttons.length; i++){
    btn_id = "btn_" + (i + 1);
    console.log(btn_id);
    price_id = "price_" +  (i + 1);
    console.log(price_id);
    buttons[i] = document.getElementById(btn_id);
    items_price[i] = document.getElementById(price_id);
    buttons[i].addEventListener("click", function() {
      
      fetch(add_to_cart_url+(i + 1),
      {
        method: 'POST',
      })
          .then((response) => {
              return response.json();
          })
          .then((myjson) => {
          if (myjson.response == 'OK')
          {
            console.log('OK')
            price += Number(items_price[i].textContent);
            tg.MainButton.setText("Итого: "+ String(price) + " Оплатить?");
            tg.MainButton.show();
            a.style.visibility = 'visible';
            a.innerHTML = "Итого: " + String(price)  + " Оплатить?";
          }
           
          });
    });
    
  }
    }
  );


  
Telegram.WebApp.onEvent("mainButtonClicked", function(){
    
    window.location.replace("/cart");
    a.style.visibility = 'hidden';
    tg.MainButton.hide();
});