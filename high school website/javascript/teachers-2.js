const cards_2 = document.querySelectorAll('.card-2');
const prevBtn_2 = document.querySelector('.prev-btn_2');
const nextBtn_2 = document.querySelector('.next-btn_2');
let cardIndex_2 = 0;

function showCards_2() {
    for (let i = 0; i < cards_2.length; i++) {
      cards_2[i].style.display = "none";
    }
    for (let i = cardIndex_2; i < cardIndex_2 + 4; i++) {
      if (cards_2[i]) {
        cards_2[i].style.display = "block";
        cards_2[i].classList.remove('left', 'right');
        if (i === cardIndex_2) {
          cards_2[i].classList.add('left');
        }
        if (i === cardIndex_2 + 3 || i === cards_2.length - 1) {
          cards_2[i].classList.add('right');
        }
      }
    }
  }

showCards_2();

prevBtn_2.addEventListener("click", () => {
  cardIndex_2 -= 1;
  if (cardIndex_2 < 0) {
    cardIndex_2 = cards_2.length - 4;
  }
  showCards_2();
});

nextBtn_2.addEventListener("click", () => {
  cardIndex_2 += 1;
  if (cardIndex_2 > cards_2.length - 4) {
    cardIndex_2 = 0;
  }
  showCards_2();
});

