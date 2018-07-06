var burgerButton = document.querySelector("#burger")
var navMenu = document.querySelector("#"+burgerButton.dataset.target);

burgerButton.addEventListener('click',function (e) {
    this.classList.toggle('is-active');
    navMenu.classList.toggle('is-active');
})
