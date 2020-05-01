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
    Nick VARCHAR2(20) NOT NULL PRIMARY KEY,
    Email VARCHAR2(50) NOT NULL,
    Password VARCHAR2(30) NOT NULL,
    Fullname VARCHAR2(50) NOT NULL,
    Location NUMBER(7) NOT NULL,
    Birthdate DATE NOT NULL,
    FOREIGN KEY (Location) REFERENCES Settlements(Id)
);

CREATE TABLE Pictures (
    Filename VARCHAR2(30) NOT NULL PRIMARY KEY,
    Author VARCHAR2(20) NOT NULL,
    Title VARCHAR2(30) NOT NULL,
    Description VARCHAR2(150),
    Location NUMBER(7),
    FOREIGN KEY (Author) REFERENCES Users(Nick),
    FOREIGN KEY (Location) REFERENCES Settlements(Id)
);

CREATE TABLE Categories (
    Name VARCHAR2(20) NOT NULL,
    Pictureid VARCHAR2(30) NOT NULL,
    FOREIGN KEY (Pictureid) REFERENCES Pictures(Filename)
);

CREATE TABLE Ratings (
    Stars NUMBER(1) NOT NULL,
    Picture VARCHAR2(30) NOT NULL,
    Usernick VARCHAR2(20) NOT NULL,
    PRIMARY KEY(Picture, Usernick),
    FOREIGN KEY (Picture) REFERENCES Pictures(Filename),
    FOREIGN KEY (Usernick) REFERENCES Users(Nick)
);

CREATE OR REPLACE TRIGGER delete_from_category
AFTER DELETE ON Pictures
FOR EACH ROW
BEGIN
    DELETE FROM Categories WHERE Pictureid = :OLD.Filename;
END;

CREATE OR REPLACE TRIGGER delete_from_ratings
AFTER DELETE ON Pictures
FOR EACH ROW
BEGIN
    DELETE FROM Ratings WHERE Picture = :OLD.Filename;
END;

CREATE OR REPLACE TRIGGER default_pic_rate
AFTER INSERT ON Pictures
FOR EACH ROW
DECLARE
    kep pictures.filename%TYPE;
    author pictures.author%TYPE;
BEGIN
    kep := :NEW.filename;
    author := :NEW.author;
    INSERT INTO Ratings Values (0, kep, author);
end;