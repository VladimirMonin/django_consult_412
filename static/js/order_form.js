// Получаем данные из data-атрибутов при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    const dataContainer = document.getElementById('order-form-data');
    const servicesUrl = dataContainer ? dataContainer.dataset.servicesUrl : '/barbershop/masters_services/';
    const csrfToken = dataContainer ? dataContainer.dataset.csrfToken : '';
    
    // Инициализация функций с полученными данными
    initOrderForm(servicesUrl, csrfToken);
});


function initOrderForm(servicesUrl, csrfToken) {
    // Функция получения услуг мастера
    async function getServicesByMasterId(masterId) {
        const response = await fetch(servicesUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ master_id: masterId })
        });
        if (!response.ok) {
            throw new Error('Статус ответа: ' + response.status);
        }
        const data = await response.json();

        return data.map(service => ({
            id: service.id,
            name: service.name
        }));
    }

    // Функция для обновления выпадающего списка услуг
    async function updateServicesDropdown(masterId) {
        try {
            // Получаем список услуг для выбранного мастера
            const services = await getServicesByMasterId(masterId);
            
            // Находим селект для услуг
            const servicesSelect = document.getElementById('id_services');
            
            // Очищаем текущие опции
            servicesSelect.innerHTML = '';
            
            // Добавляем новые опции на основе полученных данных
            services.forEach(service => {
                const option = document.createElement('option');
                option.value = service.id;
                option.textContent = service.name;
                servicesSelect.appendChild(option);
            });
            
            // Включаем мультиселект, если он был отключен
            servicesSelect.disabled = services.length === 0;
            
            // Если услуг нет, добавляем сообщение
            if (services.length === 0) {
                const option = document.createElement('option');
                option.textContent = 'У этого мастера нет услуг';
                servicesSelect.appendChild(option);
            }
        } catch (error) {
            console.error('Ошибка при получении услуг:', error);
        }
    }

    // Вешаем обработчик события на изменение выбора мастера
    document.addEventListener('DOMContentLoaded', function() {
        const masterSelect = document.getElementById('id_master');
        const servicesSelect = document.getElementById('id_services');
        
        // Если нет мастера или услуг, выходим
        if (!masterSelect || !servicesSelect) return;
        
        // Обработчик события change для выбора мастера
        masterSelect.addEventListener('change', function() {
            const masterId = this.value;
            if (masterId) {
                updateServicesDropdown(masterId);
            } else {
                // Если мастер не выбран, очищаем список услуг
                servicesSelect.innerHTML = '';
                const option = document.createElement('option');
                option.textContent = 'Сначала выберите мастера';
                servicesSelect.appendChild(option);
                servicesSelect.disabled = true;
            }
        });
        
        // При загрузке страницы проверяем, выбран ли мастер
        if (masterSelect.value) {
            updateServicesDropdown(masterSelect.value);
        } else {
            // Если мастер не выбран, показываем подсказку
            servicesSelect.innerHTML = '';
            const option = document.createElement('option');
            option.textContent = 'Сначала выберите мастера';
            servicesSelect.appendChild(option);
            servicesSelect.disabled = true;
        }
    });
    
    // Улучшим виджет выбора даты
    document.addEventListener('DOMContentLoaded', function() {
        const dateField = document.getElementById('id_appointment_date');
        if (dateField) {
            // Добавляем атрибуты для улучшения поля выбора даты
            dateField.setAttribute('type', 'datetime-local');
            
            // Устанавливаем минимальную дату (сегодня)
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            
            const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
            dateField.setAttribute('min', minDateTime);
        }
    });