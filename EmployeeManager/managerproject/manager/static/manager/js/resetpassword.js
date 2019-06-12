var password = document.getElementById("password1"), confirm_password = document.getElementById("password2");

function validatePassword(){
	if(password.value.length < 8) {
       password.setCustomValidity("A senha deve ter no mínimo 8 caracteres");  
  } else {
    if(password.value != confirm_password.value) {
    	confirm_password.setCustomValidity("As senhas devem ser iguais");
    } else {
       confirm_password.setCustomValidity('');
    }
  }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;