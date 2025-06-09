CREATE TABLE IF NOT EXISTS paises_iso (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo_iso3 CHAR(3) NOT NULL UNIQUE
);

INSERT INTO
    paises_iso (nombre, codigo_iso3)
VALUES ('Antigua y Barbuda', 'ATG'),
    ('Argentina', 'ARG'),
    ('Bahamas', 'BHS'),
    ('Barbados', 'BRB'),
    ('Belice', 'BLZ'),
    ('Bolivia', 'BOL'),
    ('Brasil', 'BRA'),
    ('Canadá', 'CAN'),
    ('Chile', 'CHL'),
    ('Colombia', 'COL'),
    ('Costa Rica', 'CRI'),
    ('Cuba', 'CUB'),
    ('Dominica', 'DMA'),
    ('Ecuador', 'ECU'),
    ('El Salvador', 'SLV'),
    ('Estados Unidos', 'USA'),
    ('Granada', 'GRD'),
    ('Guatemala', 'GTM'),
    ('Guyana', 'GUY'),
    ('Haití', 'HTI'),
    ('Honduras', 'HND'),
    ('Jamaica', 'JAM'),
    ('México', 'MEX'),
    ('Nicaragua', 'NIC'),
    ('Panamá', 'PAN'),
    ('Paraguay', 'PRY'),
    ('Perú', 'PER'),
    ('República Dominicana', 'DOM'),
    (
        'San Cristóbal y Nieves',
        'KNA'
    ),
    ('Santa Lucía', 'LCA'),
    (
        'San Vicente y las Granadinas',
        'VCT'
    ),
    ('Surinam', 'SUR'),
    ('Trinidad y Tobago', 'TTO'),
    ('Uruguay', 'URY'),
    ('Venezuela', 'VEN');