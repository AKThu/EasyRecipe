// for displaying current year in the footer
document.querySelector('#date').textContent = new Date().getFullYear();


// click to remove popup messages
Array.from(document.querySelectorAll('.toast')).map((toast) => {
    toast.addEventListener('click', (e) => {
    e.target.remove();
    });
});


// put cursor at the end of text in the search input field
const urlParams = new URLSearchParams(window.location.search);
search_input = urlParams.get('search_recipe');
document.querySelector("#search_input").value = search_input ? search_input : "";