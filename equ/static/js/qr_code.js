
const scanType = document.getElementById('scanType').value;
console.log(scanType);

document.getElementById('start-scan-btn').addEventListener('click', function(e) {
    e.preventDefault();

    document.getElementById('reader').style.display = 'block';
    document.getElementById('stop-scan-btn').style.display = 'inline-block'; // Показываем кнопку остановки

    const html5QrCode = new Html5Qrcode("reader");

    Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length) {
            devices.forEach((device, index) => {
                const option = document.createElement("option");
                option.value = device.id;
                option.text = device.label || `Камера ${index + 1}`;
                cameraSelect.appendChild(option);
            });

            const backCamera = devices.find(device => device.label.toLowerCase().includes('back'));
            const defaultCameraId = backCamera ? backCamera.id : devices[0].id;
            cameraSelect.value = defaultCameraId;
            console.log(scanType);

            html5QrCode.start(
                defaultCameraId,
                {
                    fps: 10,
                    qrbox: { width: 250, height: 250 }
                },
                success
            ).catch(err => console.log(`Ошибка запуска камеры: ${err}`));
        }
    }).catch(err => console.log(`Ошибка получения камер: ${err}`));

    cameraSelect.addEventListener("change", () => {
        const selectedCameraId = cameraSelect.value;
        html5QrCode.stop().then(() => {
            html5QrCode.start(
                selectedCameraId,
                {
                    fps: 10,
                    qrbox: { width: 250, height: 250 }
                },
                success
            ).catch(err => console.log("Ошибка при запуске сканера с новой камерой:", err));
        }).catch(err => console.log("Ошибка при остановке текущей камеры:", err));
    });

    window.html5QrCode = html5QrCode;
});
document.getElementById('stop-scan-btn').addEventListener('click', function(e) {
    e.preventDefault();

    if (window.html5QrCode) {
        window.html5QrCode.stop().then(() => {
            console.log('Сканер остановлен');
            document.getElementById('reader').style.display = 'none';
            document.getElementById('stop-scan-btn').style.display = 'none';
        }).catch(err => console.log(`Error stopping scanner: ${err}`));
    }
});

//const qrCodeUrl = "{% url 'qr_code_view' %}";
function success(decodedText, decodedResult) {
    fetch(qrCodeUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'equipment-type': scanType,
            'location': location_id,
            'X-CSRFToken': getCookie('csrftoken'),  // Если CSRF защита включена
        },
        body: JSON.stringify({ code: decodedText })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Ответ от сервера:', data);
        console.log(data.message);

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

    html5QrCode.stop().then(() => {
        document.getElementById('reader').style.display = 'none';
    }).catch(err => {
        console.error(`Ошибка при остановке сканера: ${err}`);
    });
}
