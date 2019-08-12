drop table if exists "user" cascade;
drop table if exists collections cascade;
drop table if exists object_files cascade;
drop table if exists model cascade;
drop table if exists variant cascade;
drop table if exists liveries cascade;
drop table if exists companies cascade;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'model_type') THEN
        create type model_type as enum('locomotive', 'coach', 'wagon');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'locomotive_type') THEN
        create type locomotive_type as enum('steam', 'diesel', 'electric', 'DMU', 'EMU', 'other');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'company_type') THEN
        create type company_type as enum('manufacturer', 'operator');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'object_type') THEN
        create type object_type as enum('body', 'bogies', 'coupler');
    END IF;
END$$;

create table "user" (
    id serial,
    email text unique not null,
    created timestamp not null default current_timestamp,
    last_online timestamp not null default current_timestamp,
    nickname text not null,
    password text not null,
    primary key (id)
);

create table companies (
    id serial,
    name text not null,
    company_type company_type,
    primary key (id)
);

-- one of these is made for each user as their downloads
create table collections (
    id serial,
    author_id integer not null,
    created timestamp not null default current_timestamp,
    last_updated timestamp not null default current_timestamp,
    name text not null,
    is_public boolean,
    primary key (id),
    foreign key (author_id) references "user"(id)
);

create table model (
    id serial,
    author_id integer not null,
    created timestamp not null default current_timestamp,
    last_updated timestamp not null default current_timestamp,
    title text not null,
    description text not null,
    model_type model_type,
    countries text[],
    manufacturer_ref integer,
    tags text[],
    ratings integer[],
    thumbnail_name text not null,
    thumbnail bytea not null,
    primary key (id),
    foreign key (author_id) references "user" (id),
    foreign key (manufacturer_ref) references companies(id)
);

-- keep these seperate for the models which use a common front and back value
create table object_files (
    id serial,
    object_type object_type,
    obj_file bytea not null,
    primary key (id)
);

create table variant (
    id serial,
    author_id integer not null,
    model_ref integer not null,
    created timestamp not null default current_timestamp,
    last_updated timestamp not null default current_timestamp,
    name text not null,
    description text,
    tags text[],
    ratings integer[],
    body_ref integer not null,
    bogie_front_ref integer not null,
    bogie_back_ref integer not null,
    coupler_front_ref integer not null,
    coupler_back_ref integer not null,
    config_file bytea not null,
    primary key (id),
    foreign key (author_id) references "user"(id),
    foreign key (model_ref) references model(id),
    foreign key (body_ref) references object_files(id),
    foreign key (bogie_front_ref) references object_files(id),
    foreign key (bogie_back_ref) references object_files(id),
    foreign key (coupler_front_ref) references object_files(id),
    foreign key (coupler_back_ref) references object_files(id)
);

create table liveries (
    id serial,
    author_id integer not null,
    variant_ref integer not null,
    created timestamp not null default current_timestamp,
    name text not null,
    description text,
    operator_ref integer,
    ratings integer[],
    texture_file bytea not null,
    primary key (id),
    foreign key (author_id) references "user" (id),
    foreign key (variant_ref) references variant (id),
    foreign key (operator_ref) references companies(id)
);
