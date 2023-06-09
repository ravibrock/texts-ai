SELECT m1.chat_identifier, m1.is_from_me, m1.date,
    GROUP_CONCAT(m1.text, '. ') AS text_concat
FROM (
    SELECT
        ROW_NUMBER() OVER (PARTITION BY main.chat.chat_identifier ORDER BY message.date) - ROW_NUMBER()
            OVER (PARTITION BY main.chat.chat_identifier, message.is_from_me ORDER BY message.date) AS grp,
        message_id,
        message.is_from_me,
        message.date,
        message.text,
        main.chat.chat_identifier
    FROM main.message
    JOIN chat_message_join ON chat_message_join.message_id = message.ROWID
    JOIN main.chat ON main.chat.ROWID = chat_message_join.chat_id
    WHERE main.chat.chat_identifier IN (
        SELECT chat_identifier
        FROM main.chat
        WHERE chat_identifier REGEXP '^(\+1|.*@.*)'
        AND service_name = 'iMessage'
    )
    AND message.text != ''
    AND message.text != '￼'
    AND message.text != '￼￼'
    AND message.text != '￼￼￼￼￼￼￼'
    AND message.text IS NOT NULL
    AND message.text NOT LIKE 'http%'
    AND message.text NOT LIKE 'www.%'
    AND message.text NOT REGEXP '^(Loved|Liked|Disliked|Laughed at|Emphasized|Questioned)'
    AND message.text <> '(I’m not receiving notifications. If this is urgent, reply “urgent” to send a notification through with your original message.)'
) AS m1
JOIN chat_message_join AS cmj ON cmj.message_id = m1.message_id
JOIN main.chat AS c ON c.ROWID = cmj.chat_id
GROUP BY m1.chat_identifier, m1.is_from_me, m1.grp
ORDER BY m1.chat_identifier ASC, m1.date ASC;
