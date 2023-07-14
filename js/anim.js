const navbar = document.querySelector('#nav-open');
const img = document.querySelector('img');

img.addEventListener('click', () => {
  navbar.classList.toggle('open');
});