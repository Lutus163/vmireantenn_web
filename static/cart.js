let tg = window.Telegram.WebApp;
console.log(tg.InitDataUnsafe);
tg.expand();
tg.MainButton.textColor = '#FFFFFF';
tg.MainButton.color = '#2cab37';

let total = document.getElementById("total");
let pay = document.getElementById("pay");

const amount_items_cart_url='/amount_items_cart';
const increase_amount_url='/increase_amount/';
const decrease_amount_url='/decrease_amount/';
const delete_item_url='/delete_item/';

let amount_items_cart = 0;
let price = Number(total.textContent);


fetch(amount_items_cart_url)
    .then(data => data.json())
    .then(response =>  {
      amount_items = Number(response.amount);

      let buttons_increase = new Array(amount_items);
      let buttons_decrease = new Array(amount_items);
      let buttons_delete = new Array(amount_items);

      let tbodies = new Array(amount_items);

      let items_price = new Array(amount_items);
      let items_amount = new Array(amount_items);
      let list_indexes = response.keys;


    for(let i = 0; i < buttons_increase.length; i++){
    btn_id_in = "increase_" + list_indexes[i];
    btn_id_dec = "decrease_" + list_indexes[i];
    btn_id_del = "delete_" + list_indexes[i];
    tbody_id = "tbody_" + list_indexes[i];

    price_id = "price_" +  list_indexes[i];
    amount_id = "amount_" +  list_indexes[i];
    console.log(price_id);

    buttons_increase[i] = document.getElementById(btn_id_in);
    buttons_decrease[i] = document.getElementById(btn_id_dec);
    buttons_delete[i] = document.getElementById(btn_id_del);

    tbodies[i] = document.getElementById(tbody_id);

    items_price[i] = document.getElementById(price_id);
    items_amount[i] = document.getElementById(amount_id);

    buttons_increase[i].addEventListener("click", function() {
      let index = list_indexes[i]
      fetch(increase_amount_url+index,
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
            items_amount[i].value = Number(items_amount[i].value) + 1;
            tg.MainButton.setText("Итого: "+ String(price) + " Оплатить");
            tg.MainButton.show();

            total.innerHTML = price;

            if(Number(total.textContent) > 0){
              pay.style.visibility = 'visible';
            }
          }

          });
    });
    buttons_decrease[i].addEventListener("click", function() {
      if (Number(items_amount[i].value) > 0){
      let index = list_indexes[i]
      fetch(decrease_amount_url+index,
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
            price -= Number(items_price[i].textContent);
            items_amount[i].value = Number(items_amount[i].value) - 1;
            tg.MainButton.setText("Итого: "+ String(price) + " Оплатить");
            tg.MainButton.show();

            total.innerHTML = price;
            if(Number(total.textContent) == 0){
              pay.style.visibility = 'hidden';
            }
          }

          });

      }

    });

    buttons_delete[i].addEventListener("click", function() {
      let index = list_indexes[i]
      fetch(delete_item_url+index,
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
            price -= Number(items_price[i].textContent) * Number(items_amount[i].value);
            total.innerHTML = price;
            tbodies[i].remove();
            if(Number(total.textContent) == 0){
              pay.style.visibility = 'hidden';
            }

          }

          });

      }

    );

  }




    }
  );

Telegram.WebApp.onEvent("mainButtonClicked", function(){

    window.location.replace("/buy");
    tg.MainButton.hide();
    tg.MainButton.setText("");
});