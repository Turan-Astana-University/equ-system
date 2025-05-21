const scanType = document.getElementById('scanType').value;
console.log(scanType);

const input = document.getElementById('scanner-input');

// Автофокус при загрузке
window.onload = () => {
    input.focus();
};

// Ловим скан
input.addEventListener('change', () => {
    const decodedText = input.value.trim();
    console.log("Сканировано:", decodedText);

    // Очистка поля
    input.value = '';
    input.focus();

    if (!decodedText) return;

    if (scanType === 'FindEquipment') {
        fetch(qrCodeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'equipment-type': scanType,
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ code: decodedText })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Ответ от сервера:', data);
            console.log(data.message);
            equipmentId = data.id;
            const redirectUrl = update.replace('1', equipmentId);
            window.location.href = redirectUrl;

            setTimeout(() => {
                window.location.reload();
            }, 2000);
        })
        .catch(error => {
            console.error('Ошибка при отправке данных на сервер:', error);
        });

    } else if (scanType === 'inventory') {
        fetch(qrCodeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'equipment-type': scanType,
                'location': location_id,
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ code: decodedText })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Ответ от сервера:', data);

            if (data.message === "Equipment found" && data.location_correct) {
                addRowToTable('found', data);
            } else if (data.message === "Equipment found" && !data.location_correct) {
                addRowToTable('wrong_location', data);
            } else {
                addRowToTable('not_found', data);
            }

            document.getElementById('result').innerHTML = `
                <h2>Успешно!</h2>
                <p>${data.name}, Позиция: ${data.location_correct}</p>
            `;

            setTimeout(() => {
                window.location.reload();
            }, 2000);
        })
        .catch(error => {
            console.error('Ошибка при отправке данных на сервер:', error);
        });
    }
});
