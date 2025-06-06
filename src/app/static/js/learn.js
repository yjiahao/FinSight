let btn = document.getElementById("changeBtn");

btn.addEventListener(
    'click',
    function() {
        if (this.textContent === 'Click me') {
            this.textContent = 'Clicked!';
            this.style.backgroundColor = '#e74c3c';
        } else {
            this.textContent = 'Click me';
            this.style.backgroundColor = '#3498db';
        }
    }
);

let greetBtn = document.querySelector(".test");
let input = document.getElementById("nameInput");
let output = document.getElementById("output");

greetBtn.addEventListener(
    'click',
    function() {
        output.textContent = `Hello ${input.value}`;
    }
);