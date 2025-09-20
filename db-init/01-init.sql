create schema if not exists travel_db;
CREATE TABLE if not exists travel_db.city (
    city_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS travel_db.directory_route (
    id SERIAL PRIMARY KEY,
    type_transport VARCHAR(100) NOT NULL,
    departure_city INT NOT NULL,
    arrival_city INT NOT NULL,
    distance INT NOT NULL,
    price INT NOT NULL,
    CONSTRAINT fk_departure_city FOREIGN KEY (departure_city) REFERENCES travel_db.city(city_id) ON DELETE CASCADE,
    CONSTRAINT fk_arrival_city FOREIGN KEY (arrival_city) REFERENCES travel_db.city(city_id) ON DELETE CASCADE
);

CREATE TABLE if not exists travel_db.users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    passport VARCHAR(20) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT null,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE 
);

CREATE TABLE if not exists travel_db.entertainment (
    id SERIAL PRIMARY KEY,
    duration VARCHAR(50) NOT NULL,
    address VARCHAR(255) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    event_time TIMESTAMP NOT NULL,
    city INT NOT NULL,
    CONSTRAINT fk_city FOREIGN KEY (city) REFERENCES travel_db.city(city_id) ON DELETE CASCADE
);

CREATE TABLE if not exists travel_db.accommodations (
    id SERIAL PRIMARY KEY,
    price INT NOT NULL,
    address VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    rating INT NOT NULL,
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP NOT NULL,
    city INT NOT NULL,
    CONSTRAINT fk_city FOREIGN KEY (city) REFERENCES travel_db.city(city_id) ON DELETE CASCADE
);
create table if not exists travel_db.travel (
	id SERIAL PRIMARY KEY,
	status VARCHAR(50) not null,
	user_id int not null,
    CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES travel_db.users(id) ON DELETE CASCADE 
);

create table if not exists travel_db.route (
	id SERIAL PRIMARY KEY,
	d_route_id INT not null,
	travel_id INT not null,
	start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT null,
    type VARCHAR(20) NOT null,
    CONSTRAINT fk_d_route_id FOREIGN KEY (d_route_id) REFERENCES travel_db.directory_route(id) ON DELETE CASCADE,
    CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel_db.travel(id) ON DELETE CASCADE
	
	-- CONSTRAINT fk_d_route_id FOREIGN KEY (d_route_id) REFERENCES travel_db.directory_route(id),
	-- CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel_db.travel(id)
);


create table if not exists travel_db.travel_entertainment (
	id SERIAL PRIMARY KEY,
	travel_id INT not null,
	entertainment_id int not null,
    CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel_db.travel(id) ON DELETE CASCADE,
    CONSTRAINT fk_entertainment_id FOREIGN KEY (entertainment_id) REFERENCES travel_db.entertainment(id) ON DELETE CASCADE
	-- CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel_db.travel(id),
	-- CONSTRAINT fk_entertainment_id FOREIGN KEY (entertainment_id) REFERENCES travel_db.entertainment(id)
);

create table if not exists travel_db.travel_accommodations (
	id SERIAL PRIMARY KEY,
	travel_id INT not null,
	accommodation_id int not null,
    CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel_db.travel(id) ON DELETE CASCADE,
    CONSTRAINT fk_accommodation_id FOREIGN KEY (accommodation_id) REFERENCES travel_db.accommodations(id) ON DELETE CASCADE
	-- CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel_db.travel(id),
	-- CONSTRAINT accommodation_id FOREIGN KEY (accommodation_id) REFERENCES travel_db.accommodations(id)
);

create table if not exists travel_db.users_travel(
    id SERIAL PRIMARY KEY,
    travel_id INT NOT NULL,
    users_id INT NOT NULL,
    CONSTRAINT fk_travel_id FOREIGN KEY (travel_id) REFERENCES travel_db.travel(id) ON DELETE CASCADE,
    CONSTRAINT fk_users_id FOREIGN KEY (users_id) REFERENCES travel_db.users(id) ON DELETE CASCADE
)
