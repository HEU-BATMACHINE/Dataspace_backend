-- init.sql
CREATE TABLE IF NOT EXISTS Dryer1_Bottom_ActTemperature (
    time TIMESTAMPTZ  NOT NULL,
    Dryer1_Bottom_ActTemperature DOUBLE PRECISION NOT NULL
);
CREATE TABLE IF NOT EXISTS Dryer1_Top_ActTemperature (
    time TIMESTAMPTZ  NOT NULL,
    Dryer1_Top_ActTemperature DOUBLE PRECISION NOT NULL
);
CREATE TABLE IF NOT EXISTS Anode_Thickness (
    time TIMESTAMPTZ  NOT NULL,
    Anode_Thickness DOUBLE PRECISION NOT NULL
);

-- Add any other initialization queries here
-- Load the TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Convert the sensor_data table into a hypertable
SELECT create_hypertable('Dryer1_Bottom_ActTemperature', 'time');
SELECT create_hypertable('Dryer1_Top_ActTemperature', 'time');
SELECT create_hypertable('Anode_Thickness', 'time');

INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T09:51:03.694629+00:00', 298.234);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T09:52:03.694629+00:00', 298.334);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T09:53:03.694629+00:00', 298.434);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T09:54:03.694629+00:00', 298.534);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T09:55:03.694629+00:00', 298.634);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T09:56:03.694629+00:00', 298.534);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T09:57:03.694629+00:00', 298.434);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T09:58:03.694629+00:00', 298.534);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T09:59:03.694629+00:00', 298.634);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T10:00:03.694629+00:00', 298.734);
INSERT INTO Dryer1_Bottom_ActTemperature (time, Dryer1_Bottom_ActTemperature) VALUES ('2024-03-13T10:01:03.694629+00:00', 298.834);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T09:51:03.694629+00:00', 303.1);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T09:52:03.694629+00:00', 304.2);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T09:53:03.694629+00:00', 305.3);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T09:54:03.694629+00:00', 304.4);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T09:55:03.694629+00:00', 302.5);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T09:56:03.694629+00:00', 301.6);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T09:57:03.694629+00:00', 300.7);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T09:58:03.694629+00:00', 298.8);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T09:59:03.694629+00:00', 295.9);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T10:00:03.694629+00:00', 297.0);
INSERT INTO Dryer1_Top_ActTemperature (time, Dryer1_Top_ActTemperature) VALUES ('2024-03-13T10:01:03.694629+00:00', 298.1);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T09:51:03.694629+00:00', 0.000051);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T09:52:03.694629+00:00', 0.000052);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T09:53:03.694629+00:00', 0.000053);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T09:54:03.694629+00:00', 0.000053);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T09:55:03.694629+00:00', 0.000053);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T09:56:03.694629+00:00', 0.000053);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T09:57:03.694629+00:00', 0.000053);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T09:58:03.694629+00:00', 0.000053);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T09:59:03.694629+00:00', 0.000053);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T10:00:03.694629+00:00', 0.000052);
INSERT INTO Anode_Thickness (time, Anode_Thickness) VALUES ('2024-03-13T10:01:03.694629+00:00', 0.000052);
