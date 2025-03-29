$(document).ready(function() {
$("#email").inputmask({
    alias: "email",
    placeholder: "x@x.x",
    definitions: {
      'x': {
        validator: "[A-Za-z0-9@.\-]",
        casing: "lower"
      }
    }
  });
});
  $(document).ready(function() {
    $("#phone").inputmask({
      mask: "+7(9##)###-##-##",
      definitions: {
        '#': {
          validator: "[0-9]",
          cardinality: 1
        },
        '9': {
          validator: "9",
          cardinality: 1
        }
      }
    });
  });