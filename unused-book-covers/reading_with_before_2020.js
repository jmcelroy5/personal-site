function showBooks(matchFunc) {
  let count = 0;
  document.querySelectorAll('.reading-list-item').forEach(item => {
    if (matchFunc(item.dataset.year)) {
      item.style.display = 'block';
      count++;
    }
  });
  document.getElementById("book-count").innerHTML = `${count} books`
}

function enableNavBtns(year) {
  const prevYearBtn = document.getElementById("prev-year");
  if (year === "before-2020") {
    prevYearBtn.disabled = true;
  } else {
    prevYearBtn.style.display = "block";
    prevYearBtn.addEventListener("click", () => {
      window.location = year !== "2020"
        ? `/reading/${Number(year) - 1}`
        : "before-2020"

    })
  }

  const nextYearBtn = document.getElementById("next-year");
  if (Number(year) !== new Date().getFullYear()) {
    nextYearBtn.style.display = "block";
    nextYearBtn.addEventListener("click", () => {
      window.location = year !== "before-2020"
        ? `/reading/${Number(year) + 1}`
        : "/reading/2021"
    })
  } else {
    nextYearBtn.disabled = true;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  const yearStr = path.split('/').pop();
  const yearNum = Number(yearStr);

  if (yearStr) {
    if (yearStr === "before-2020") {
      showBooks((y) => y < 2020)
      document.getElementById("year").innerHTML = "Favs from before 2020"
      enableNavBtns(yearStr);
    } else if (yearNum >= 2020) {
      showBooks((y) => y === yearStr)
      document.getElementById("year").innerHTML = yearStr
      enableNavBtns(yearStr);
    }
  }
})