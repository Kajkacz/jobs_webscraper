-- Created by Vertabelo (http://vertabelo.com)
-- Last modification date: 2021-11-01 10:55:47.825

-- tables
-- Table: City
CREATE TABLE City (
    CityId int  NOT NULL,
    City varchar(100)  NOT NULL,
    Country_CountryID int  NOT NULL,
    CONSTRAINT City_pk PRIMARY KEY (CityId)
);

-- Table: Company
CREATE TABLE Company (
    CompanyId int  NOT NULL,
    CompanyName varchar(100)  NOT NULL,
    CONSTRAINT Company_pk PRIMARY KEY (CompanyId)
);

-- Table: Country
CREATE TABLE Country (
    CountryID int  NOT NULL,
    Country varchar(100)  NOT NULL,
    CONSTRAINT Country_pk PRIMARY KEY (CountryID)
);

-- Table: Date
CREATE TABLE Date (
    DateId int  NOT NULL,
    Day int  NOT NULL,
    DayOfWeek int  NOT NULL,
    Month int  NOT NULL,
    Year int  NOT NULL,
    Hour int  NOT NULL,
    Minute int  NOT NULL,
    Second int  NOT NULL,
    CONSTRAINT Date_pk PRIMARY KEY (DateId)
);

-- Table: District
CREATE TABLE District (
    DistrictID int  NOT NULL,
    District varchar(100)  NOT NULL,
    City_CityId int  NOT NULL,
    CONSTRAINT District_pk PRIMARY KEY (DistrictID)
);

-- Table: Location
CREATE TABLE Location (
    LocationID int  NOT NULL,
    Address varchar(100)  NOT NULL,
    District_DistrictID int  NOT NULL,
    CONSTRAINT Location_pk PRIMARY KEY (LocationID)
);

-- Table: Offer
CREATE TABLE Offer (
    OfferID int  NOT NULL,
    Position_PositionID int  NOT NULL,
    Company_CompanyId int  NOT NULL,
    Date_DateId int  NOT NULL,
    Salary_Salary_ID int  NOT NULL,
    Location_LocationID int  NOT NULL,
    CONSTRAINT Offer_pk PRIMARY KEY (OfferID)
);

-- Table: Position
CREATE TABLE Position (
    PositionID int  NOT NULL,
    "Level" int  NOT NULL,
    Position int  NOT NULL,
    CONSTRAINT Position_pk PRIMARY KEY (PositionID)
);

-- Table: Salary
CREATE TABLE Salary (
    upper_range_uop int  NOT NULL,
    lower_range_uop int  NOT NULL,
    upper_range_b2b int  NOT NULL,
    lower_range_b2b int  NOT NULL,
    average_uop int  NOT NULL,
    average_b2b int  NOT NULL,
    Salary_ID int  NOT NULL,
    CONSTRAINT Salary_pk PRIMARY KEY (Salary_ID)
);

-- Table: Skill
CREATE TABLE Skill (
    SkillID int  NOT NULL,
    Skill int  NOT NULL,
    CONSTRAINT Skill_pk PRIMARY KEY (SkillID)
);

-- Table: SkillOffer
CREATE TABLE SkillOffer (
    "Level" int  NOT NULL,
    SkillOfferID int  NOT NULL,
    Skill_SkillID int  NOT NULL,
    Offer_OfferID int  NOT NULL,
    CONSTRAINT SkillOffer_pk PRIMARY KEY (SkillOfferID)
);

-- -- foreign keys
-- -- Reference: City_Country (table: City)
-- ALTER TABLE City ADD CONSTRAINT City_Country
--     FOREIGN KEY (Country_CountryID)
--     REFERENCES Country (CountryID)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- Reference: District_City (table: District)
-- ALTER TABLE District ADD CONSTRAINT District_City
--     FOREIGN KEY (City_CityId)
--     REFERENCES City (CityId)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- Reference: Location_District (table: Location)
-- ALTER TABLE Location ADD CONSTRAINT Location_District
--     FOREIGN KEY (District_DistrictID)
--     REFERENCES District (DistrictID)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- Reference: Offer_Company (table: Offer)
-- ALTER TABLE Offer ADD CONSTRAINT Offer_Company
--     FOREIGN KEY (Company_CompanyId)
--     REFERENCES Company (CompanyId)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- Reference: Offer_Date (table: Offer)
-- ALTER TABLE Offer ADD CONSTRAINT Offer_Date
--     FOREIGN KEY (Date_DateId)
--     REFERENCES Date (DateId)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- Reference: Offer_Location (table: Offer)
-- ALTER TABLE Offer ADD CONSTRAINT Offer_Location
--     FOREIGN KEY (Location_LocationID)
--     REFERENCES Location (LocationID)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- Reference: Offer_Position (table: Offer)
-- ALTER TABLE Offer ADD CONSTRAINT Offer_Position
--     FOREIGN KEY (Position_PositionID)
--     REFERENCES Position (PositionID)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- Reference: Offer_Salary (table: Offer)
-- ALTER TABLE Offer ADD CONSTRAINT Offer_Salary
--     FOREIGN KEY (Salary_Salary_ID)
--     REFERENCES Salary (Salary_ID)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- Reference: SkillOffer_Offer (table: SkillOffer)
-- ALTER TABLE SkillOffer ADD CONSTRAINT SkillOffer_Offer
--     FOREIGN KEY (Offer_OfferID)
--     REFERENCES Offer (OfferID)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- Reference: SkillOffer_Skill (table: SkillOffer)
-- ALTER TABLE SkillOffer ADD CONSTRAINT SkillOffer_Skill
--     FOREIGN KEY (Skill_SkillID)
--     REFERENCES Skill (SkillID)  
--     NOT DEFERRABLE 
--     INITIALLY IMMEDIATE
-- ;

-- -- sequences
-- -- Sequence: City_seq
-- CREATE SEQUENCE City_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: Company_seq
-- CREATE SEQUENCE Company_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: Country_seq
-- CREATE SEQUENCE Country_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: Date_seq
-- CREATE SEQUENCE Date_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: District_seq
-- CREATE SEQUENCE District_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: Location_seq
-- CREATE SEQUENCE Location_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: Offer_seq
-- CREATE SEQUENCE Offer_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: Position_seq
-- CREATE SEQUENCE Position_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: Salary_seq
-- CREATE SEQUENCE Salary_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: SkillOffer_seq
-- CREATE SEQUENCE SkillOffer_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- -- Sequence: Skill_seq
-- CREATE SEQUENCE Skill_seq
--       INCREMENT BY 1
--       NO MINVALUE
--       NO MAXVALUE
--       START WITH 1
--       NO CYCLE
-- ;

-- End of file.

