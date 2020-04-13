CREATE TABLE Countries (
    Id NUMBER(4) NOT NULL PRIMARY KEY,
    Name VARCHAR2(50) NOT NULL,
    Continent VARCHAR2(50)NOT NULL,
    Flag VARCHAR2(10) NOT NULL
);

CREATE TABLE Settlements (
    Id NUMBER(7) NOT NULL PRIMARY KEY,
    Name VARCHAR2(50) NOT NULL,
    Country NUMBER(4) NOT NULL,
    FOREIGN KEY (Country) REFERENCES Countries(Id)
);

CREATE TABLE Users (
    Id NUMBER(10) NOT NULL PRIMARY KEY,
    Email VARCHAR2(50) NOT NULL,
    Password VARCHAR2(30) NOT NULL,
    Nick VARCHAR2(20) NOT NULL,
    Fullname VARCHAR2(50) NOT NULL,
    Location NUMBER(7) NOT NULL,
    Birthdate DATE NOT NULL,
    FOREIGN KEY (Location) REFERENCES Settlements(Id)
);

CREATE TABLE Pictures (
    Filename VARCHAR2(20) NOT NULL PRIMARY KEY,
    Title VARCHAR2(30) NOT NULL,
    Description VARCHAR2(150),
    Location NUMBER(7),
    FOREIGN KEY (Location) REFERENCES Settlements(Id)
);

CREATE TABLE Categories (
    Name VARCHAR2(20) NOT NULL,
    Pictureid VARCHAR2(20) NOT NULL,
    FOREIGN KEY (Pictureid) REFERENCES Pictures(Filename)
);

CREATE TABLE Ratings (
    Stars NUMBER(1) NOT NULL,
    Picture VARCHAR2(20) NOT NULL,
    Userid NUMBER(10) NOT NULL,
    PRIMARY KEY(Picture, Userid),
    FOREIGN KEY (Picture) REFERENCES Pictures(Filename),
    FOREIGN KEY (Userid) REFERENCES Users(Id)
);
