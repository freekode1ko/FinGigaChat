let currentUrl = window.location.href;
let regex = /\/meeting.*/;
let url = currentUrl.replace(regex, "");

let tg = window.Telegram.WebApp;
tg.expand();

//if (tg.initData == '') {
//    $('body').empty();
//}

let user_id = tg.initDataUnsafe.user?.id;
fetchData(user_id);


async function fetchData(user_id) {

    try {
        const response = await fetch(`${url}/meeting/show/${user_id}`);
        const responseData = await response.json();

        if (responseData.length == 0) {
            const deleteElement = document.querySelector("#container");
            deleteElement.innerHTML = '';
            $('#noMeeting').text('У Вас пока нет новых встреч');
            return;
        }

        $('#noMeeting').text('');
        $.each(responseData, function(index, meeting) {
            $('#meetingTable tbody').
            append('<tr><td>' + meeting.theme + '</td><td>' + meeting.date_start + '</td></tr>');
        });

    } catch (error) {
        console.error("Ошибка при получении данных:", error);
        const deleteElement = document.querySelector("#container");
        deleteElement.innerHTML = '';
    }
};

