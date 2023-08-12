$(document).ready(function(){
    const readMoreBtn = document.querySelector('.read-button');
    const text = document.querySelector('.text');

    readMoreBtn.addEventListener('click', (e)=>{
        text.classList.toggle('show-more');
    });
});