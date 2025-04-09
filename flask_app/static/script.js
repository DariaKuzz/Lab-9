document.addEventListener("DOMContentLoaded", () => {
    const stepList = document.getElementById("stepList");
    const stepForm = document.getElementById("stepForm");

    // Функция загрузки списка шагов
    function loadSteps() {
        fetch("/api/steps")
            .then(response => response.json())
            .then(steps => {
                stepList.innerHTML = "";
                steps.forEach(step => {
                    const li = document.createElement("li");
                    li.innerHTML = `Дата: ${step.date}, Шаги: ${step.steps} 
                        <button onclick="deleteStep('${step.date}')">❌</button>`;
                    stepList.appendChild(li);
                });
            })
            .catch(error => console.error("Ошибка загрузки:", error));
    }

    // Добавление записи о шагах
    stepForm.addEventListener("submit", event => {
        event.preventDefault();
        const date = document.getElementById("date").value;
        const steps = document.getElementById("steps").value;

        fetch("/api/steps", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ date, steps: parseInt(steps) })
        })
        .then(response => {
            if (!response.ok) throw new Error("Ошибка сервера");
            return response.json();
        })
        .then(() => {
            stepForm.reset();
            loadSteps();
            updateTotalSteps();
        })
        .catch(error => console.error("Ошибка:", error));
    });

    // Удаление записи
    window.deleteStep = (date) => {
        if (confirm("Удалить эту запись?")) {
            fetch(`/api/steps/${date}`, { 
                method: "DELETE" 
            })
            .then(() => {
                loadSteps()
                updateTotalSteps();})
            .catch(error => console.error("Ошибка удаления:", error));
        }
    };
    
    // Функция обновления суммы
async function updateTotalSteps() {
    try {
        const response = await fetch('/api/steps/total');
        const data = await response.json();
        document.getElementById('totalSteps').textContent = data.total_steps;
    } catch (error) {
        console.error('Ошибка загрузки суммы:', error);
    }
}

// Вызывать при загрузке и после изменений
document.addEventListener('DOMContentLoaded', () => {
    updateTotalSteps();
});

    // Загрузка данных при загрузке страницы
    loadSteps();
    updateTotalSteps();
});