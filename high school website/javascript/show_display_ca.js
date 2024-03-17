const button = document.getElementById("title");
const myDiv = document.getElementById("tabla");
const button_ceac = document.getElementById("title-ceac");
const myDiv_ceac = document.getElementById("tabla-ceac");
const title = document.getElementById("titlu")
const title_ceac = document.getElementById("titlu-ceac")
let isShowing = false;

button.addEventListener("click", function() {
  do {
    if (isShowing) {
      myDiv.classList.remove("show");
      title.style.textDecoration = ("none");
      isShowing = false;
    } else {
      myDiv.classList.add("show");
      isShowing = true;
      title.style.textDecoration = ("underline");
    }
  } while (false);
});
button_ceac.addEventListener("click", function() {
  do {
    if (isShowing) {
      myDiv_ceac.classList.remove("show");
      title_ceac.style.textDecoration = ("none");
      isShowing = false;
    } else {
      myDiv_ceac.classList.add("show");
      title_ceac.style.textDecoration = ("underline");
      isShowing = true;
    }
  } while (false);
});