async def add_notify_job(logger: Logger.logger, meeting: Optional[dict[str, Any]] = None):
    meetings = [meeting, ] if meeting else await get_user_meetings_for_notification()
    for rem_time_dict in REMEMBER_TIME.values():
        for meeting in meetings:
            dt_notification = meeting['date_start'] + dt.timedelta(hours=meeting['timezone'])
            dt_notification -= dt.timedelta(minutes=rem_time_dict['minutes'])
            if dt_notification < dt.datetime.now():
                continue
            scheduler.add_job(
                send_notification,
                args=(logger, meeting['meeting_id'], meeting['user_id'], meeting['theme'],
                      meeting['date_start'], rem_time_dict['msg']),
                trigger='date',
                run_date=dt_notification,
                timezone='Europe/Moscow'
            )
            logger.info('Для пользователя %s добавлена задача-напоминание в %s', meeting['user_id'], dt_notification)