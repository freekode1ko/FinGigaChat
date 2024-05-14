let currentUrl = window.location.href;
let regex = /\/meeting.*/;
let url = currentUrl.replace(regex, "");

let tg = window.Telegram.WebApp;

//if (tg.initDataUnsafe == '') {
//    $('body').empty();
//}

let user_id = tg?.initDataUnsafe?.user?.id;

let backPageHref = `${url}/meeting/show`;

const curDate = new Date();
const curYear = curDate.getFullYear();
let dateStart = new Date();
let dateEnd = new Date();

let dateStartField = document.getElementById('date-start');
let dateEndField = document.getElementById('date-end');
let timeStartField = document.getElementById('time-start');
let timeEndField = document.getElementById('time-end');


let dateStartRoll = new Rolldate({
                                    el: dateStartField,
                                    format: 'DD-MM-YYYY',
                                    beginYear: curYear,
                                    endYear: curYear + 1,
                                    lang: { title: "Выбор даты" },
                                    init: function() {
                                        document.activeElement.blur();
                                    },
                                    confirm: function(date) {
                                        $('#errorMessageDateStart').text("");
                                        let [day, month, year] = date.split('-');
                                        dateStart.setFullYear(parseInt(year, 10));
                                        dateStart.setMonth(parseInt(month, 10) - 1);
                                        dateStart.setDate(parseInt(day, 10));
                                        dateEndField.value = date;
                                        }
                                    });


let dateEndRoll = new Rolldate({
                                el: dateEndField,
                                format: 'DD-MM-YYYY',
                                beginYear: curYear,
                                endYear: curYear + 1,
                                lang: { title: "Выбор даты"},
                                init: function() {
                                     document.activeElement.blur();
                                },
                                confirm: function(date) {
                                    $('#errorMessageDateStart').text("");
                                }
                                });


let timeStartRoll = new Rolldate({
                                    el: timeStartField,
                                    format: 'hh:mm',
                                    lang: { title: "Выбор времени"},
                                    init: function() {
                                        document.activeElement.blur();
                                    },
                                    confirm: function(time) {
                                        $('#errorMessageDateStart').text("");
                                        timeEndField.disabled = false;
                                        let [hours, minutes] = time.split(':');
                                        dateStart.setHours(parseInt(hours, 10));
                                        dateStart.setMinutes(parseInt(minutes, 10));

                                        let defaultTime = moment(dateStart).add(30, 'm').toDate();
                                        let defaultHour = defaultTime.getHours().toString().padStart(2, '0');
                                        let defaultMinutes = defaultTime.getMinutes().toString().padStart(2, '0');
                                        timeEndField.value = `${defaultHour}:${defaultMinutes}`;
                                    }
                                    });


let timeEndRoll = new Rolldate({
                                el: timeEndField,
                                format: 'hh:mm',
                                lang: { title: "Выбор времени"},
                                init: function() {
                                      document.activeElement.blur();
                                },
                                confirm: function(date) {
                                    $('#errorMessageDateStart').text("");
                                }
                               });


function postData(user_data) {

    return new Promise(function(resolve, reject) {
        let query = `?user_id=${user_id}&theme=${user_data.theme}&` +
                    `date_start=${user_data.date_start}&date_end=${user_data.date_end}&` +
                    `description=${user_data.description}&timezone=${user_data.timezone}`;

        fetch(`${url}/meeting/save${query}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка при отправке данных на сервер: ' + response.statusText);
                }
                return response.text();
            })
            .then(data => {
                resolve(data);
            })
            .catch(error => {
                reject(error);
            });
    });
};

$('#back').click(function(event) {
    window.location.href = backPageHref;
})


$('#create').click(function(event) {
    event.preventDefault();

    let [day, month, year] = dateEndField.value.split('-');
    dateEnd.setFullYear(parseInt(year, 10));
    dateEnd.setMonth(parseInt(month, 10) - 1);
    dateEnd.setDate(parseInt(day, 10));
    let [hoursEnd, minutesEnd] = timeEndField.value.split(':');
    dateEnd.setHours(parseInt(hoursEnd, 10));
    dateEnd.setMinutes(parseInt(minutesEnd, 10));

    $('#errorMessageDateStart').text('');
    $('#errorMessageTheme').text('');

    if (dateStartField.value === '') {
        event.preventDefault();
        $('#errorMessageDateStart').text('Заполните время начала встречи');
        return;
    }
    if ($('#theme').val().trim() === '') {
        event.preventDefault();
        $('#errorMessageTheme').text('Заполните тему встречи');
        return;
    }

    if (dateEnd.getTime() <= dateStart.getTime() || isNaN(dateEnd)) {
         dateEndField.value = "";
         timeEndField.value = "";
          $('#errorMessageDateStart').text('Дата окончания заполнена некорректно');
          return;
    }

    if (dateStart.getTime() < curDate.getTime()) {
         $('#errorMessageDateStart').text('Дата уже прошла');
         return;
    }

    let meeting_data = {
        theme: $('#theme').val(),
        date_start: dateStart.toISOString(),
        date_end: dateEnd.toISOString(),
        description: $('#description').val() || '',
        timezone: new Date().getTimezoneOffset()
    };


    postData(meeting_data).
        then(function(response) {
            console.log('Данные успешно отправлены на сервер');
            $('form')[0].reset();
            window.location.href = backPageHref;
        })
        .catch(function(error) {
            console.error('Ошибка при отправке данных на сервер:', error);
        });

});
