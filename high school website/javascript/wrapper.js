const wraper = document.querySelector(".wraper");
const button = document.querySelector(".accept-button");

button.addEventListener("click", () => {
    wraper.classList.remove("active");
    localStorage.setItem("GDPRBannerDisplayed", "true");
});


setTimeout(() => {
    if(!localStorage.getItem("GDPRBannerDisplayed")){
    wraper.classList.add("active");
    }
}, 2000);
