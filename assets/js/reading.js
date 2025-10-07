(function () {
  const CURRENT_YEAR = new Date().getFullYear();
  const CUTOFF_YEAR = 2021;
  const BOOK_COUNT_EL_ID = 'book-count';
  const YEAR_EL_ID = 'year';
  const PREV_YEAR_BTN_ID = 'prev-year';
  const NEXT_YEAR_BTN_ID = 'next-year';
  const BOOK_CLASS = '.reading-list-item'

  function showBooks(yearStr) {
    let count = 0;
    document.querySelectorAll(BOOK_CLASS).forEach(item => {
      if (item.dataset.year === yearStr) {
        item.style.display = 'block';
        count++;
      }
    });
    document.getElementById(BOOK_COUNT_EL_ID).innerHTML = `${count} books`
  }

  function enableNavBtns(yearNum) {
    const prevYearBtn = document.getElementById(PREV_YEAR_BTN_ID);
    const nextYearBtn = document.getElementById(NEXT_YEAR_BTN_ID);

    if (yearNum !== CUTOFF_YEAR) {
      prevYearBtn.style.display = 'block';
      prevYearBtn.addEventListener('click', () => {
        window.location = `/reading?year=${yearNum - 1}`

      })
    } else {
      prevYearBtn.disabled = true;
    }

    if (yearNum !== CURRENT_YEAR) {
      nextYearBtn.style.display = 'block';
      nextYearBtn.addEventListener('click', () => {
        window.location = `/reading?year=${yearNum + 1}`
      })
    } else {
      nextYearBtn.disabled = true;
    }
  }

  window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const yearStr = urlParams.get('year') || CURRENT_YEAR.toString();
    const yearNum = Number(yearStr);

    if (yearNum >= CUTOFF_YEAR) {
      showBooks(yearStr)
      enableNavBtns(yearNum);
      document.getElementById(YEAR_EL_ID).innerHTML = yearStr
    }
  })
})()