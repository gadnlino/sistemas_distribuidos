-- Atenção!!!!!
-- Para que o script python de criação funcione, é necessário deixar um comando por linha

DROP TABLE IF EXISTS topic;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS message;
DROP TABLE IF EXISTS subscription;
DROP TABLE IF EXISTS publication;
DROP TABLE IF EXISTS message_delivery;

CREATE TABLE topic (topic_id integer PRIMARY KEY AUTOINCREMENT, topic_name text, old_topic_name text, creator_id integer, enabled integer);

CREATE TABLE user (user_id integer PRIMARY KEY AUTOINCREMENT,user_name text, logged_in integer);

CREATE TABLE message (message_id integer PRIMARY KEY AUTOINCREMENT,timestamp real, message_body text);

CREATE TABLE subscription (subscription_id integer PRIMARY KEY AUTOINCREMENT,topic_id integer,subscriber_id integer);

CREATE TABLE publication (publication_id integer PRIMARY KEY AUTOINCREMENT,topic_id integer,publisher_id integer, message_id integer);

CREATE TABLE message_delivery (message_delivery_id integer PRIMARY KEY AUTOINCREMENT,message_id integer, recipient_id integer, delivery_timestamp real);





