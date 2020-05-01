//lekérjük a ratings értékeit vagyis a csillagokat
let stars = document.querySelectorAll('.ratings .fa');
let ratingValue = document.querySelector(".ratingValue");
let index, currentStars;
for (let i = 0; i < stars.length; i++) {
    <!-- Ha az egeret rávisszük akk jelölje ki a csillagokat-->
    stars[i].addEventListener("mouseover", function () {
        currentStars = i % 5;
        for (let j = i-currentStars; j <= i; j++) {
            stars[j].classList.remove("fa-star-o");
            stars[j].classList.add("fa-star");
        }
    });
    stars[i].addEventListener("click", function () {
        ratingValue.value = i + 1;
        index = i;
    })
    // ha kikattintunk akkor is maradjanak meg a pontozott részek
    stars[i].addEventListener("mouseout", function () {
        for (let j = 0; j < stars.length; j++) {
            stars[j].classList.remove("fa-star");
            stars[j].classList.add("fa-star-o");
        }
        for (let j = index-currentStars; j <= index; j++) {
            stars[j].classList.remove("fa-star-o");
            stars[j].classList.add("fa-star");
        }
    })
}