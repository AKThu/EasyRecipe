// for displaying current year in the footer
document.querySelector('#date').textContent = new Date().getFullYear();


// click to remove popup messages
Array.from(document.querySelectorAll('.toast')).map((toast) => {
    toast.addEventListener('click', (e) => {
    e.target.remove();
    });
});


// 