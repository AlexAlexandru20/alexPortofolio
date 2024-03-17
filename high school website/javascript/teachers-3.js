const cards_3 = document.querySelectorAll('.card-3');
const prevBtn_3 = document.querySelector('.prev-btn_3');
const nextBtn_3 = document.querySelector('.next-btn_3');
let cardIndex_3 = 0;

function showCards_3() {
    for (let i = 0; i < cards_3.length; i++) {
      cards_3[i].style.display = "none";
    }
    for (let i = cardIndex_3; i < cardIndex_3 + 4; i++) {
      if (cards_3[i]) {
        cards_3[i].style.display = "block";
        cards_3[i].classList.remove('left', 'right');
        if (i === cardIndex_3) {
          cards_3[i].classList.add('left');
        }
        if (i === cardIndex_3 + 3 || i === cards_3.length - 1) {
          cards_3[i].classList.add('right');
        }
      }
    }
  }

showCards_3();

prevBtn_3.addEventListener("click", () => {
  cardIndex_3 -= 1;
  if (cardIndex_3 < 0) {
    cardIndex_3 = cards_3.length - 4;
  }
  showCards_3();
});

nextBtn_3.addEventListener("click", () => {
  cardIndex_3 += 1;
  if (cardIndex_3 > cards_3.length - 4) {
    cardIndex_3 = 0;
  }
  showCards_3();
});

