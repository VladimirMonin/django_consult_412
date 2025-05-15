// Модульная структура для order_form.js
// Все функции объявлены отдельно, логирование на каждом этапе

// Защита от двойной инициализации - предотвращает повторное выполнение скрипта
// если он по какой-то причине загружен дважды (проблема с кешированием или двойным подключением)
if (window._orderFormInitialized) {
  console.warn("order_form.js уже инициализирован!");
} else {
  window._orderFormInitialized = true;
  // Получаем данные из data-атрибутов HTML-элемента
  // Эта функция извлекает URL для API и CSRF-токен из специального контейнера в DOM
  function getConfig() {
    const dataContainer = document.getElementById("order-form-data");
    if (!dataContainer) {
      console.error("order-form-data не найден!");
      // Запасной вариант, если контейнер с данными не найден
      return { servicesUrl: "/barbershop/masters_services/", csrfToken: "" };
    }
    console.log("Конфиг успешно получен из data-атрибутов");
    return {
      // URL для запроса услуг мастера через AJAX
      servicesUrl: dataContainer.dataset.servicesUrl,
      // CSRF-токен для защиты от подделки запросов
      csrfToken: dataContainer.dataset.csrfToken,
    };
  }
  // Асинхронная функция для получения услуг мастера по его ID через AJAX
  // Использует Fetch API для отправки POST-запроса на сервер
  async function getServicesByMasterId(masterId, servicesUrl, csrfToken) {
    console.log(`Запрашиваем услуги для мастера с id=${masterId}`);
    try {
      // Отправляем POST-запрос на сервер Django
      const response = await fetch(servicesUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json", // Формат данных - JSON
          "X-CSRFToken": csrfToken, // Защита от CSRF-атак
        },
        // Передаём ID мастера в теле запроса
        body: JSON.stringify({ master_id: masterId }),
      });
      // Проверяем статус ответа
      if (!response.ok) {
        throw new Error("Статус ответа: " + response.status);
      }
      // Преобразуем ответ в JSON
      const data = await response.json();
      console.log("Получены услуги:", data);
      // Преобразуем данные в удобный формат для работы в JS
      return data.map((service) => ({ id: service.id, name: service.name }));
    } catch (error) {
      // Обрабатываем возможные ошибки при запросе
      console.error("Ошибка при получении услуг:", error);
      return []; // Возвращаем пустой массив в случае ошибки
    }
  }

  // Асинхронная функция для обновления выпадающего списка услуг
  // в зависимости от выбранного мастера
  async function updateServicesDropdown(masterId, servicesUrl, csrfToken) {
    // Находим элемент select для услуг по его ID
    const servicesSelect = document.getElementById("id_services");
    if (!servicesSelect) {
      console.error("Селект услуг не найден!");
      return;
    }
    // Очищаем список услуг перед добавлением новых
    // Это предотвращает дублирование услуг при повторном выборе мастера
    console.log("Очищаю список услуг перед обновлением");
    servicesSelect.innerHTML = "";

    // Если мастер не выбран, показываем подсказку
    if (!masterId) {
      const option = document.createElement("option");
      option.textContent = "Сначала выберите мастера";
      servicesSelect.appendChild(option);
      servicesSelect.disabled = true; // Делаем селект неактивным
      console.log("Мастер не выбран, услуги не обновлены");
      return;
    } // Получаем услуги выбранного мастера через асинхронный запрос
    const services = await getServicesByMasterId(
      masterId,
      servicesUrl,
      csrfToken
    );
    console.log("Добавляю услуги в селект:", services);

    // Если у мастера нет услуг, показываем соответствующее сообщение
    if (services.length === 0) {
      const option = document.createElement("option");
      option.textContent = "У этого мастера нет услуг";
      servicesSelect.appendChild(option);
      servicesSelect.disabled = true; // Делаем селект неактивным
      console.log("У выбранного мастера нет услуг");
      return;
    }

    // Добавляем каждую услугу в выпадающий список
    services.forEach((service) => {
      const option = document.createElement("option");
      option.value = service.id; // ID услуги для отправки на сервер
      option.textContent = service.name; // Название услуги для отображения
      servicesSelect.appendChild(option);
    });

    // Активируем селект после добавления услуг
    servicesSelect.disabled = false;
    console.log(
      "Список услуг успешно обновлён. Текущее количество опций:",
      servicesSelect.options.length
    );
  }
  // Инициализация обработчиков событий для формы заказа
  // Главная функция, которая устанавливает все слушатели событий
  function initOrderForm() {
    // Получаем конфигурацию (URL API и CSRF-токен)
    const { servicesUrl, csrfToken } = getConfig();

    // Находим элементы формы
    const masterSelect = document.getElementById("id_master");
    const servicesSelect = document.getElementById("id_services");

    // Проверяем, что нужные элементы существуют на странице
    if (!masterSelect || !servicesSelect) {
      console.error("Не найден селект мастера или услуг!");
      return;
    }

    // Устанавливаем обработчик события изменения выбранного мастера
    masterSelect.addEventListener("change", function () {
      console.log("Изменён мастер:", this.value);
      // Обновляем список услуг при выборе нового мастера
      updateServicesDropdown(this.value, servicesUrl, csrfToken);
    });

    // Инициализируем список услуг при первой загрузке страницы
    if (masterSelect.value) {
      // Если мастер уже выбран (например, при редактировании заказа)
      updateServicesDropdown(masterSelect.value, servicesUrl, csrfToken);
    } else {
      // Если мастер не выбран, показываем подсказку
      updateServicesDropdown(null, servicesUrl, csrfToken);
    }
  }
  // Улучшение виджета выбора даты и времени
  // Django по умолчанию не создаёт удобный datetime-local инпут,
  // эта функция превращает обычное текстовое поле в специальный виджет для даты и времени
  function enhanceDateField() {
    // Находим поле для выбора даты записи
    const dateField = document.getElementById("id_appointment_date");
    if (!dateField) {
      console.warn("Поле даты не найдено");
      return;
    }

    // Меняем тип поля на datetime-local для удобного выбора даты и времени
    dateField.setAttribute("type", "datetime-local");

    // Получаем текущую дату и время для установки минимальной даты записи
    // (чтобы нельзя было выбрать прошедшее время)
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0"); // +1 т.к. месяцы с 0
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");

    // Форматируем дату и время в строку формата YYYY-MM-DDThh:mm
    const minDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;

    // Устанавливаем минимальную дату для выбора (нельзя записаться "в прошлое")
    dateField.setAttribute("min", minDateTime);
    console.log("Виджет даты улучшен");
  }
  // Главная точка входа - запускается после полной загрузки DOM
  // Это необходимо, чтобы быть уверенным, что все HTML-элементы уже существуют
  document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM полностью загружен, инициализируем форму заказа...");
    // Инициализируем зависимость услуг от выбранного мастера
    initOrderForm();
    // Улучшаем виджет выбора даты
    enhanceDateField();
  });
}
