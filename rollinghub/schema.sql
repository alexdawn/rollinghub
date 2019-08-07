drop table if exists "user" cascade;
drop table if exists mod cascade;

create table "user" (
    id serial,
    username text unique not null,
    password text not null,
    primary key (id)
);

create table mod (
    id serial,
    author_id integer not null,
    created timestamp not null default current_timestamp,
    title text not null,
    description text not null,
    primary key (id),
    foreign key (author_id) references "user" (id)
);