const cards = document.querySelectorAll('.card');
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');
let cardIndex = 0;

function showCards() {
    for (let i = 0; i < cards.length; i++) {
      cards[i].style.display = "none";
    }
    for (let i = cardIndex; i < cardIndex + 4; i++) {
      if (cards[i]) {
        cards[i].style.display = "block";
        cards[i].classList.remove('left', 'right');
        if (i === cardIndex) {
          cards[i].classList.add('left');
        }
        if (i === cardIndex + 3 || i === cards.length - 1) {
          cards[i].classList.add('right');
        }
      }
    }
  }
  
  

showCards();

prevBtn.addEventListener("click", () => {
  cardIndex -= 1;
  if (cardIndex < 0) {
    cardIndex = cards.length - 4;
  }
  showCards();
});

nextBtn.addEventListener("click", () => {
  cardIndex += 1;
  if (cardIndex > cards.length - 4) {
    cardIndex = 0;
  }
  showCards();
});