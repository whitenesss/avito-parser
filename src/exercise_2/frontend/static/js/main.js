document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const statusDiv = document.getElementById('status');
    statusDiv.textContent = 'Загрузка...';
    statusDiv.className = '';

    const fileInput = document.getElementById('xmlFile');
    const file = fileInput.files[0];

    if (!file) {
        statusDiv.textContent = 'Выберите файл для загрузки';
        statusDiv.className = 'error';
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,

        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сервера');
        }

        const result = await response.json();
        statusDiv.textContent = `Файл ${result.filename} успешно загружен (${result.size} байт)`;
        statusDiv.className = 'success';
    } catch (error) {
        statusDiv.textContent = `Ошибка: ${error.message}`;
        statusDiv.className = 'error';
        console.error('Upload error:', error);
    }
});