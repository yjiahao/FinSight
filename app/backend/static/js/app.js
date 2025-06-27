const input = document.getElementById("taskInput");
const button = document.getElementById("addTask");
const taskList = document.getElementById("taskList");

button.addEventListener("click", () => {
  const taskText = input.value;

  if (taskText === "") return;

  const li = document.createElement("li");

  // Create a span to hold the task text
  const taskSpan = document.createElement("span");
  taskSpan.textContent = taskText;

  // Optional: Click task to strike through
  taskSpan.addEventListener("click", () => {
    taskSpan.style.textDecoration = "line-through";
  });

  // Create delete button
  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "❌";
  deleteBtn.style.marginLeft = "10px";

  // Delete this task when clicked
  deleteBtn.addEventListener("click", () => {
    li.remove(); // Removes the whole list item
  });

  // Append both span and delete button to the list item
  li.appendChild(taskSpan);
  li.appendChild(deleteBtn);

  // Add to the list
  taskList.appendChild(li);
  input.value = "";
});

input.addEventListener(
    "keydown",
    function(event) {
        if (event.key === "Enter") {
            const taskText = input.value;

            if (taskText === "") return;

            const li = document.createElement("li");

            // Create a span to hold the task text
            const taskSpan = document.createElement("span");
            taskSpan.textContent = taskText;

            // Optional: Click task to strike through
            taskSpan.addEventListener("click", () => {
                taskSpan.style.textDecoration = "line-through";
            });

            // Create delete button
            const deleteBtn = document.createElement("button");
            deleteBtn.textContent = "❌";
            deleteBtn.style.marginLeft = "10px";

            // Delete this task when clicked
            deleteBtn.addEventListener("click", () => {
                li.remove(); // Removes the whole list item
            });

            // Append both span and delete button to the list item
            li.appendChild(taskSpan);
            li.appendChild(deleteBtn);

            // Add to the list
            taskList.appendChild(li);
            input.value = "";
        }
    }
);