CREATE TABLE municipios (
    codigo VARCHAR(4) PRIMARY KEY,
    vecindad VARCHAR(150),
    municipio VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL
);

CREATE UNIQUE INDEX idx_codigo ON municipios (codigo);

ALTER TABLE municipios ADD CONSTRAINT unique_codigo UNIQUE (codigo);

ALTER TABLE municipios ADD COLUMN datos JSONB;

INSERT INTO
    municipios (
        codigo,
        vecindad,
        municipio,
        departamento
    )
VALUES (
        '0101',
        'Guatemala, Guatemala',
        'Guatemala',
        'Guatemala'
    ),
    (
        '0102',
        'Santa Catarina Pinula, Guatemala',
        'Santa Catarina Pinula',
        'Guatemala'
    ),
    (
        '0103',
        'San José Pinula, Guatemala',
        'San José Pinula',
        'Guatemala'
    ),
    (
        '0104',
        'San José del Golfo, Guatemala',
        'San José del Golfo',
        'Guatemala'
    ),
    (
        '0105',
        'Palencia, Guatemala',
        'Palencia',
        'Guatemala'
    ),
    (
        '0106',
        'Chinautla, Guatemala',
        'Chinautla',
        'Guatemala'
    ),
    (
        '0107',
        'San Pedro Ayampuc, Guatemala',
        'San Pedro Ayampuc',
        'Guatemala'
    ),
    (
        '0108',
        'Mixco, Guatemala',
        'Mixco',
        'Guatemala'
    ),
    (
        '0109',
        'San Pedro Sacatepéquez, Guatemala',
        'San Pedro Sacatepéquez',
        'Guatemala'
    ),
    (
        '0110',
        'San Juan Sacatepéquez, Guatemala',
        'San Juan Sacatepéquez',
        'Guatemala'
    ),
    (
        '0111',
        'San Raymundo, Guatemala',
        'San Raymundo',
        'Guatemala'
    ),
    (
        '0112',
        'Chuarrancho, Guatemala',
        'Chuarrancho',
        'Guatemala'
    ),
    (
        '0113',
        'Fraijanes, Guatemala',
        'Fraijanes',
        'Guatemala'
    ),
    (
        '0114',
        'Amatitlán, Guatemala',
        'Amatitlán',
        'Guatemala'
    ),
    (
        '0115',
        'Villa Nueva, Guatemala',
        'Villa Nueva',
        'Guatemala'
    ),
    (
        '0116',
        'Villa Canales, Guatemala',
        'Villa Canales',
        'Guatemala'
    ),
    (
        '0117',
        'San Miguel Petapa, Guatemala',
        'San Miguel Petapa',
        'Guatemala'
    ),
    (
        '0201',
        'Guastatoya, El Progreso',
        'Guastatoya',
        'ElProgreso'
    ),
    (
        '0202',
        'Morazán, El Progreso',
        'Morazán',
        'ElProgreso'
    ),
    (
        '0203',
        'San Agustín Acasaguastlán, El Progreso',
        'San Agustín Acasaguastlán',
        'ElProgreso'
    ),
    (
        '0204',
        'San Cristóbal Acasaguastlán, El Progreso',
        'San Cristóbal Acasaguastlán',
        'ElProgreso'
    ),
    (
        '0205',
        'El Jícaro, El Progreso',
        'El Jícaro',
        'ElProgreso'
    ),
    (
        '0206',
        'Sansare, El Progreso',
        'Sansare',
        'ElProgreso'
    ),
    (
        '0207',
        'Sanarate, El Progreso',
        'Sanarate',
        'ElProgreso'
    ),
    (
        '0208',
        'San Antonio La Paz, El Progreso',
        'San Antonio La Paz',
        'ElProgreso'
    ),
    (
        '0301',
        'Antigua Guatemala, Sacatepéquez',
        'Antigua Guatemala',
        'Sacatepéquez'
    ),
    (
        '0302',
        'Jocotenango, Sacatepéquez',
        'Jocotenango',
        'Sacatepéquez'
    ),
    (
        '0303',
        'Pastores, Sacatepéquez',
        'Pastores',
        'Sacatepéquez'
    ),
    (
        '0304',
        'Sumpango, Sacatepéquez',
        'Sumpango',
        'Sacatepéquez'
    ),
    (
        '0305',
        'Santo Domingo Xenacoj, Sacatepéquez',
        'Santo Domingo Xenacoj',
        'Sacatepéquez'
    ),
    (
        '0306',
        'Santiago Sacatepéquez, Sacatepéquez',
        'Santiago Sacatepéquez',
        'Sacatepéquez'
    ),
    (
        '0307',
        'San Bartolomé Milpas Altas, Sacatepéquez',
        'San Bartolomé Milpas Altas',
        'Sacatepéquez'
    ),
    (
        '0308',
        'San Lucas Sacatepéquez, Sacatepéquez',
        'San Lucas Sacatepéquez',
        'Sacatepéquez'
    ),
    (
        '0309',
        'Santa Lucía Milpas Altas, Sacatepéquez',
        'Santa Lucía Milpas Altas',
        'Sacatepéquez'
    ),
    (
        '0310',
        'Magdalena Milpas Altas, Sacatepéquez',
        'Magdalena Milpas Altas',
        'Sacatepéquez'
    ),
    (
        '0311',
        'Santa María de Jesús, Sacatepéquez',
        'Santa María de Jesús',
        'Sacatepéquez'
    ),
    (
        '0312',
        'Ciudad Vieja, Sacatepéquez',
        'Ciudad Vieja',
        'Sacatepéquez'
    ),
    (
        '0313',
        'San Miguel Dueñas, Sacatepéquez',
        'San Miguel Dueñas',
        'Sacatepéquez'
    ),
    (
        '0314',
        'San Juan Alotenango, Sacatepéquez',
        'San Juan Alotenango',
        'Sacatepéquez'
    ),
    (
        '0315',
        'San Antonio Aguas Calientes, Sacatepéquez',
        'San Antonio Aguas Calientes',
        'Sacatepéquez'
    ),
    (
        '0316',
        'Santa Catarina Barahona, Sacatepéquez',
        'Santa Catarina Barahona',
        'Sacatepéquez'
    ),
    (
        '0401',
        'Chimaltenango, Chimaltenango',
        'Chimaltenango',
        'Chimaltenango'
    ),
    (
        '0402',
        'San José Poaquil, Chimaltenango',
        'San José Poaquil',
        'Chimaltenango'
    ),
    (
        '0403',
        'San Martín Jilotepeque, Chimaltenango',
        'San Martín Jilotepeque',
        'Chimaltenango'
    ),
    (
        '0404',
        'San Juan Comalapa, Chimaltenango',
        'San Juan Comalapa',
        'Chimaltenango'
    ),
    (
        '0405',
        'Santa Apolonia, Chimaltenango',
        'Santa Apolonia',
        'Chimaltenango'
    ),
    (
        '0406',
        'Tecpán Guatemala, Chimaltenango',
        'Tecpán Guatemala',
        'Chimaltenango'
    ),
    (
        '0407',
        'Patzún, Chimaltenango',
        'Patzún',
        'Chimaltenango'
    ),
    (
        '0408',
        'San Miguel Pochuta, Chimaltenango',
        'San Miguel Pochuta',
        'Chimaltenango'
    ),
    (
        '0409',
        'Patzicía, Chimaltenango',
        'Patzicía',
        'Chimaltenango'
    ),
    (
        '0410',
        'Santa Cruz Balanyá, Chimaltenango',
        'Santa Cruz Balanyá',
        'Chimaltenango'
    ),
    (
        '0411',
        'Acatenango, Chimaltenango',
        'Acatenango',
        'Chimaltenango'
    ),
    (
        '0412',
        'San Pedro Yepocapa, Chimaltenango',
        'San Pedro Yepocapa',
        'Chimaltenango'
    ),
    (
        '0413',
        'San Andrés Itzapa, Chimaltenango',
        'San Andrés Itzapa',
        'Chimaltenango'
    ),
    (
        '0414',
        'Parramos, Chimaltenango',
        'Parramos',
        'Chimaltenango'
    ),
    (
        '0415',
        'Zaragoza, Chimaltenango',
        'Zaragoza',
        'Chimaltenango'
    ),
    (
        '0416',
        'El Tejar, Chimaltenango',
        'El Tejar',
        'Chimaltenango'
    ),
    (
        '0501',
        'Escuintla, Escuintla',
        'Escuintla',
        'Escuintla'
    ),
    (
        '0502',
        'Santa Lucía Cotzumalguapa, Escuintla',
        'Santa Lucía Cotzumalguapa',
        'Escuintla'
    ),
    (
        '0503',
        'La Democracia, Escuintla',
        'La Democracia',
        'Escuintla'
    ),
    (
        '0504',
        'Siquinalá, Escuintla',
        'Siquinalá',
        'Escuintla'
    ),
    (
        '0505',
        'Masagua, Escuintla',
        'Masagua',
        'Escuintla'
    ),
    (
        '0506',
        'Tiquisate, Escuintla',
        'Tiquisate',
        'Escuintla'
    ),
    (
        '0507',
        'La Gomera, Escuintla',
        'La Gomera',
        'Escuintla'
    ),
    (
        '0508',
        'Guanagazapa, Escuintla',
        'Guanagazapa',
        'Escuintla'
    ),
    (
        '0509',
        'San José, Escuintla',
        'San José',
        'Escuintla'
    ),
    (
        '0510',
        'Iztapa, Escuintla',
        'Iztapa',
        'Escuintla'
    ),
    (
        '0511',
        'Palín, Escuintla',
        'Palín',
        'Escuintla'
    ),
    (
        '0512',
        'San Vicente Pacaya, Escuintla',
        'San Vicente Pacaya',
        'Escuintla'
    ),
    (
        '0513',
        'Nueva Concepción, Escuintla',
        'Nueva Concepción',
        'Escuintla'
    ),
    (
        '0514',
        'Sipacate, Escuintla',
        'Sipacate',
        'Escuintla'
    ),
    (
        '0601',
        'Cuilapa, Santa Rosa',
        'Cuilapa',
        'SantaRosa'
    ),
    (
        '0602',
        'Barberena, Santa Rosa',
        'Barberena',
        'SantaRosa'
    ),
    (
        '0603',
        'Santa Rosa de Lima, Santa Rosa',
        'Santa Rosa de Lima',
        'SantaRosa'
    ),
    (
        '0604',
        'Casillas, Santa Rosa',
        'Casillas',
        'SantaRosa'
    ),
    (
        '0605',
        'San Rafael Las Flores, Santa Rosa',
        'San Rafael Las Flores',
        'SantaRosa'
    ),
    (
        '0606',
        'Oratorio, Santa Rosa',
        'Oratorio',
        'SantaRosa'
    ),
    (
        '0607',
        'San Juan Tecuaco, Santa Rosa',
        'San Juan Tecuaco',
        'SantaRosa'
    ),
    (
        '0608',
        'Chiquimulilla, Santa Rosa',
        'Chiquimulilla',
        'SantaRosa'
    ),
    (
        '0609',
        'Taxisco, Santa Rosa',
        'Taxisco',
        'SantaRosa'
    ),
    (
        '0610',
        'Santa María Ixhuatán, Santa Rosa',
        'Santa María Ixhuatán',
        'SantaRosa'
    ),
    (
        '0611',
        'Guazacapán, Santa Rosa',
        'Guazacapán',
        'SantaRosa'
    ),
    (
        '0612',
        'Santa Cruz Naranjo, Santa Rosa',
        'Santa Cruz Naranjo',
        'SantaRosa'
    ),
    (
        '0613',
        'Pueblo Nuevo Viñas, Santa Rosa',
        'Pueblo Nuevo Viñas',
        'SantaRosa'
    ),
    (
        '0614',
        'Nueva Santa Rosa, Santa Rosa',
        'Nueva Santa Rosa',
        'SantaRosa'
    ),
    (
        '0701',
        'Sololá, Sololá',
        'Sololá',
        'Sololá'
    ),
    (
        '0702',
        'San José Chacayá, Sololá',
        'San José Chacayá',
        'Sololá'
    ),
    (
        '0703',
        'Santa María Visitación, Sololá',
        'Santa María Visitación',
        'Sololá'
    ),
    (
        '0704',
        'Santa Lucía Utatlán, Sololá',
        'Santa Lucía Utatlán',
        'Sololá'
    ),
    (
        '0705',
        'Nahualá, Sololá',
        'Nahualá',
        'Sololá'
    ),
    (
        '0706',
        'Santa Catarina Ixtahuacán, Sololá',
        'Santa Catarina Ixtahuacán',
        'Sololá'
    ),
    (
        '0707',
        'Santa Clara La Laguna, Sololá',
        'Santa Clara La Laguna',
        'Sololá'
    ),
    (
        '0708',
        'Concepción, Sololá',
        'Concepción',
        'Sololá'
    ),
    (
        '0709',
        'San Andrés Semetabaj, Sololá',
        'San Andrés Semetabaj',
        'Sololá'
    ),
    (
        '0710',
        'Panajachel, Sololá',
        'Panajachel',
        'Sololá'
    ),
    (
        '0711',
        'Santa Catarina Palopó, Sololá',
        'Santa Catarina Palopó',
        'Sololá'
    ),
    (
        '0712',
        'San Antonio Palopó, Sololá',
        'San Antonio Palopó',
        'Sololá'
    ),
    (
        '0713',
        'San Lucas Tolimán, Sololá',
        'San Lucas Tolimán',
        'Sololá'
    ),
    (
        '0714',
        'Santa Cruz La Laguna, Sololá',
        'Santa Cruz La Laguna',
        'Sololá'
    ),
    (
        '0715',
        'San Pablo La Laguna, Sololá',
        'San Pablo La Laguna',
        'Sololá'
    ),
    (
        '0716',
        'San Marcos La Laguna, Sololá',
        'San Marcos La Laguna',
        'Sololá'
    ),
    (
        '0717',
        'San Juan La Laguna, Sololá',
        'San Juan La Laguna',
        'Sololá'
    ),
    (
        '0718',
        'San Pedro La Laguna, Sololá',
        'San Pedro La Laguna',
        'Sololá'
    ),
    (
        '0719',
        'Santiago Atitlán, Sololá',
        'Santiago Atitlán',
        'Sololá'
    ),
    (
        '0801',
        'Totonicapán, Totonicapán',
        'Totonicapán',
        'Totonicapán'
    ),
    (
        '0802',
        'San Cristóbal Totonicapán, Totonicapán',
        'San Cristóbal Totonicapán',
        'Totonicapán'
    ),
    (
        '0803',
        'San Francisco El Alto, Totonicapán',
        'San Francisco El Alto',
        'Totonicapán'
    ),
    (
        '0804',
        'San Andrés Xecul, Totonicapán',
        'San Andrés Xecul',
        'Totonicapán'
    ),
    (
        '0805',
        'Momostenango, Totonicapán',
        'Momostenango',
        'Totonicapán'
    ),
    (
        '0806',
        'Santa María Chiquimula, Totonicapán',
        'Santa María Chiquimula',
        'Totonicapán'
    ),
    (
        '0807',
        'Santa Lucía la Reforma, Totonicapán',
        'Santa Lucía la Reforma',
        'Totonicapán'
    ),
    (
        '0808',
        'San Bartolo Aguas Calientes, Totonicapán',
        'San Bartolo Aguas Calientes',
        'Totonicapán'
    ),
    (
        '0901',
        'Quetzaltenango, Quetzaltenango',
        'Quetzaltenango',
        'Quetzaltenango'
    ),
    (
        '0902',
        'Salcajá, Quetzaltenango',
        'Salcajá',
        'Quetzaltenango'
    ),
    (
        '0903',
        'San Juan Olintepeque, Quetzaltenango',
        'San Juan Olintepeque',
        'Quetzaltenango'
    ),
    (
        '0904',
        'San Carlos Sija, Quetzaltenango',
        'San Carlos Sija',
        'Quetzaltenango'
    ),
    (
        '0905',
        'Sibilia, Quetzaltenango',
        'Sibilia',
        'Quetzaltenango'
    ),
    (
        '0906',
        'Cabricán, Quetzaltenango',
        'Cabricán',
        'Quetzaltenango'
    ),
    (
        '0907',
        'Cajolá, Quetzaltenango',
        'Cajolá',
        'Quetzaltenango'
    ),
    (
        '0908',
        'San Miguel Siguilá, Quetzaltenango',
        'San Miguel Siguilá',
        'Quetzaltenango'
    ),
    (
        '0909',
        'San Juan Ostuncalco, Quetzaltenango',
        'San Juan Ostuncalco',
        'Quetzaltenango'
    ),
    (
        '0910',
        'San Mateo, Quetzaltenango',
        'San Mateo',
        'Quetzaltenango'
    ),
    (
        '0911',
        'Concepción Chiquirichapa, Quetzaltenango',
        'Concepción Chiquirichapa',
        'Quetzaltenango'
    ),
    (
        '0912',
        'San Martín Sacatepéquez, Quetzaltenango',
        'San Martín Sacatepéquez',
        'Quetzaltenango'
    ),
    (
        '0913',
        'Almolonga, Quetzaltenango',
        'Almolonga',
        'Quetzaltenango'
    ),
    (
        '0914',
        'Cantel, Quetzaltenango',
        'Cantel',
        'Quetzaltenango'
    ),
    (
        '0915',
        'Huitán, Quetzaltenango',
        'Huitán',
        'Quetzaltenango'
    ),
    (
        '0916',
        'Zunil, Quetzaltenango',
        'Zunil',
        'Quetzaltenango'
    ),
    (
        '0917',
        'Colomba Costa Cuca, Quetzaltenango',
        'Colomba Costa Cuca',
        'Quetzaltenango'
    ),
    (
        '0918',
        'San Francisco La Unión, Quetzaltenango',
        'San Francisco La Unión',
        'Quetzaltenango'
    ),
    (
        '0919',
        'El Palmar, Quetzaltenango',
        'El Palmar',
        'Quetzaltenango'
    ),
    (
        '0920',
        'Coatepeque, Quetzaltenango',
        'Coatepeque',
        'Quetzaltenango'
    ),
    (
        '0921',
        'Génova, Quetzaltenango',
        'Génova',
        'Quetzaltenango'
    ),
    (
        '0922',
        'Flores Costa Cuca, Quetzaltenango',
        'Flores Costa Cuca',
        'Quetzaltenango'
    ),
    (
        '0923',
        'La Esperanza, Quetzaltenango',
        'La Esperanza',
        'Quetzaltenango'
    ),
    (
        '0924',
        'Palestina de Los Altos, Quetzaltenango',
        'Palestina de Los Altos',
        'Quetzaltenango'
    ),
    (
        '1001',
        'Mazatenango, Suchitepéquez',
        'Mazatenango',
        'Suchitepéquez'
    ),
    (
        '1002',
        'Cuyotenango, Suchitepéquez',
        'Cuyotenango',
        'Suchitepéquez'
    ),
    (
        '1003',
        'San Francisco Zapotitlán, Suchitepéquez',
        'San Francisco Zapotitlán',
        'Suchitepéquez'
    ),
    (
        '1004',
        'San Bernardino, Suchitepéquez',
        'San Bernardino',
        'Suchitepéquez'
    ),
    (
        '1005',
        'San José el Ídolo, Suchitepéquez',
        'San José el Ídolo',
        'Suchitepéquez'
    ),
    (
        '1006',
        'Santo Domingo Suchitepéquez, Suchitepéquez',
        'Santo Domingo Suchitepéquez',
        'Suchitepéquez'
    ),
    (
        '1007',
        'San Lorenzo, Suchitepéquez',
        'San Lorenzo',
        'Suchitepéquez'
    ),
    (
        '1008',
        'Samayac, Suchitepéquez',
        'Samayac',
        'Suchitepéquez'
    ),
    (
        '1009',
        'San Pablo Jocopilas, Suchitepéquez',
        'San Pablo Jocopilas',
        'Suchitepéquez'
    ),
    (
        '1010',
        'San Antonio Suchitepéquez, Suchitepéquez',
        'San Antonio Suchitepéquez',
        'Suchitepéquez'
    ),
    (
        '1011',
        'San Miguel Panán, Suchitepéquez',
        'San Miguel Panán',
        'Suchitepéquez'
    ),
    (
        '1012',
        'San Gabriel, Suchitepéquez',
        'San Gabriel',
        'Suchitepéquez'
    ),
    (
        '1013',
        'Chicacao, Suchitepéquez',
        'Chicacao',
        'Suchitepéquez'
    ),
    (
        '1014',
        'Patulul, Suchitepéquez',
        'Patulul',
        'Suchitepéquez'
    ),
    (
        '1015',
        'Santa Bárbara, Suchitepéquez',
        'Santa Bárbara',
        'Suchitepéquez'
    ),
    (
        '1016',
        'San Juan Bautista, Suchitepéquez',
        'San Juan Bautista',
        'Suchitepéquez'
    ),
    (
        '1017',
        'Santo Tomas La Unión, Suchitepéquez',
        'Santo Tomas La Unión',
        'Suchitepéquez'
    ),
    (
        '1018',
        'Zunilito, Suchitepéquez',
        'Zunilito',
        'Suchitepéquez'
    ),
    (
        '1019',
        'Pueblo Nuevo, Suchitepéquez',
        'Pueblo Nuevo',
        'Suchitepéquez'
    ),
    (
        '1020',
        'Río Bravo, Suchitepéquez',
        'Río Bravo',
        'Suchitepéquez'
    ),
    (
        '1021',
        'San José La Máquina, Suchitepéquez',
        'San José La Máquina',
        'Suchitepéquez'
    ),
    (
        '1101',
        'Retalhuleu, Retalhuleu',
        'Retalhuleu',
        'Retalhuleu'
    ),
    (
        '1102',
        'San Sebastián, Retalhuleu',
        'San Sebastián',
        'Retalhuleu'
    ),
    (
        '1103',
        'Santa Cruz Muluá, Retalhuleu',
        'Santa Cruz Muluá',
        'Retalhuleu'
    ),
    (
        '1104',
        'San Martín Zapotitlán, Retalhuleu',
        'San Martín Zapotitlán',
        'Retalhuleu'
    ),
    (
        '1105',
        'San Felipe, Retalhuleu',
        'San Felipe',
        'Retalhuleu'
    ),
    (
        '1106',
        'San Andrés Villa Seca, Retalhuleu',
        'San Andrés Villa Seca',
        'Retalhuleu'
    ),
    (
        '1107',
        'Champerico, Retalhuleu',
        'Champerico',
        'Retalhuleu'
    ),
    (
        '1108',
        'Nuevo San Carlos, Retalhuleu',
        'Nuevo San Carlos',
        'Retalhuleu'
    ),
    (
        '1109',
        'El Asintal, Retalhuleu',
        'El Asintal',
        'Retalhuleu'
    ),
    (
        '1201',
        'San Marcos, San Marcos',
        'San Marcos',
        'SanMarcos'
    ),
    (
        '1202',
        'San Pedro Sacatepéquez, San Marcos',
        'San Pedro Sacatepéquez',
        'SanMarcos'
    ),
    (
        '1203',
        'San Antonio Sacatepéquez, San Marcos',
        'San Antonio Sacatepéquez',
        'SanMarcos'
    ),
    (
        '1204',
        'Comitancillo, San Marcos',
        'Comitancillo',
        'SanMarcos'
    ),
    (
        '1205',
        'San Miguel Ixtahuacán, San Marcos',
        'San Miguel Ixtahuacán',
        'SanMarcos'
    ),
    (
        '1206',
        'Concepción Tutuapa, San Marcos',
        'Concepción Tutuapa',
        'SanMarcos'
    ),
    (
        '1207',
        'Tacaná, San Marcos',
        'Tacaná',
        'SanMarcos'
    ),
    (
        '1208',
        'Sibinal, San Marcos',
        'Sibinal',
        'SanMarcos'
    ),
    (
        '1209',
        'Tajumulco, San Marcos',
        'Tajumulco',
        'SanMarcos'
    ),
    (
        '1210',
        'Tejutla, San Marcos',
        'Tejutla',
        'SanMarcos'
    ),
    (
        '1211',
        'San Rafael Pie de la Cuesta, San Marcos',
        'San Rafael Pie de la Cuesta',
        'SanMarcos'
    ),
    (
        '1212',
        'Nuevo Progreso, San Marcos',
        'Nuevo Progreso',
        'SanMarcos'
    ),
    (
        '1213',
        'El Tumbador, San Marcos',
        'El Tumbador',
        'SanMarcos'
    ),
    (
        '1214',
        'San José el Rodeo, San Marcos',
        'San José el Rodeo',
        'SanMarcos'
    ),
    (
        '1215',
        'Malacatán, San Marcos',
        'Malacatán',
        'SanMarcos'
    ),
    (
        '1216',
        'Catarina, San Marcos',
        'Catarina',
        'SanMarcos'
    ),
    (
        '1217',
        'Ayutla, San Marcos',
        'Ayutla',
        'SanMarcos'
    ),
    (
        '1218',
        'Ocós, San Marcos',
        'Ocós',
        'SanMarcos'
    ),
    (
        '1219',
        'San Pablo, San Marcos',
        'San Pablo',
        'SanMarcos'
    ),
    (
        '1220',
        'El Quetzal, San Marcos',
        'El Quetzal',
        'SanMarcos'
    ),
    (
        '1221',
        'La Reforma, San Marcos',
        'La Reforma',
        'SanMarcos'
    ),
    (
        '1222',
        'Pajapita, San Marcos',
        'Pajapita',
        'SanMarcos'
    ),
    (
        '1223',
        'Ixchiguán, San Marcos',
        'Ixchiguán',
        'SanMarcos'
    ),
    (
        '1224',
        'San José Ojetenam, San Marcos',
        'San José Ojetenam',
        'SanMarcos'
    ),
    (
        '1225',
        'San Cristóbal Cucho, San Marcos',
        'San Cristóbal Cucho',
        'SanMarcos'
    ),
    (
        '1226',
        'Sipacapa, San Marcos',
        'Sipacapa',
        'SanMarcos'
    ),
    (
        '1227',
        'Esquipulas Palo Gordo, San Marcos',
        'Esquipulas Palo Gordo',
        'SanMarcos'
    ),
    (
        '1228',
        'Río Blanco, San Marcos',
        'Río Blanco',
        'SanMarcos'
    ),
    (
        '1229',
        'San Lorenzo, San Marcos',
        'San Lorenzo',
        'SanMarcos'
    ),
    (
        '1230',
        'La Blanca, San Marcos',
        'La Blanca',
        'SanMarcos'
    ),
    (
        '1301',
        'Huehuetenango, Huehuetenango',
        'Huehuetenango',
        'Huehuetenango'
    ),
    (
        '1302',
        'Chiantla, Huehuetenango',
        'Chiantla',
        'Huehuetenango'
    ),
    (
        '1303',
        'Malacatancito, Huehuetenango',
        'Malacatancito',
        'Huehuetenango'
    ),
    (
        '1304',
        'Cuilco, Huehuetenango',
        'Cuilco',
        'Huehuetenango'
    ),
    (
        '1305',
        'Nentón, Huehuetenango',
        'Nentón',
        'Huehuetenango'
    ),
    (
        '1306',
        'San Pedro Necta, Huehuetenango',
        'San Pedro Necta',
        'Huehuetenango'
    ),
    (
        '1307',
        'Jacaltenango, Huehuetenango',
        'Jacaltenango',
        'Huehuetenango'
    ),
    (
        '1308',
        'San Pedro Soloma, Huehuetenango',
        'San Pedro Soloma',
        'Huehuetenango'
    ),
    (
        '1309',
        'San Ildefonso Ixtahuacán, Huehuetenango',
        'San Ildefonso Ixtahuacán',
        'Huehuetenango'
    ),
    (
        '1310',
        'Santa Bárbara, Huehuetenango',
        'Santa Bárbara',
        'Huehuetenango'
    ),
    (
        '1311',
        'La Libertad, Huehuetenango',
        'La Libertad',
        'Huehuetenango'
    ),
    (
        '1312',
        'La Democracia, Huehuetenango',
        'La Democracia',
        'Huehuetenango'
    ),
    (
        '1313',
        'San Miguel Acatán, Huehuetenango',
        'San Miguel Acatán',
        'Huehuetenango'
    ),
    (
        '1314',
        'San Rafael La Independencia, Huehuetenango',
        'San Rafael La Independencia',
        'Huehuetenango'
    ),
    (
        '1315',
        'Todos Santos Cuchumatán, Huehuetenango',
        'Todos Santos Cuchumatán',
        'Huehuetenango'
    ),
    (
        '1316',
        'San Juan Atitán, Huehuetenango',
        'San Juan Atitán',
        'Huehuetenango'
    ),
    (
        '1317',
        'Santa Eulalia, Huehuetenango',
        'Santa Eulalia',
        'Huehuetenango'
    ),
    (
        '1318',
        'San Mateo Ixtatán, Huehuetenango',
        'San Mateo Ixtatán',
        'Huehuetenango'
    ),
    (
        '1319',
        'Colotenango, Huehuetenango',
        'Colotenango',
        'Huehuetenango'
    ),
    (
        '1320',
        'San Sebastián Huehuetenango, Huehuetenango',
        'San Sebastián Huehuetenango',
        'Huehuetenango'
    ),
    (
        '1321',
        'Tectitán, Huehuetenango',
        'Tectitán',
        'Huehuetenango'
    ),
    (
        '1322',
        'Concepción Huista, Huehuetenango',
        'Concepción Huista',
        'Huehuetenango'
    ),
    (
        '1323',
        'San Juan Ixcoy, Huehuetenango',
        'San Juan Ixcoy',
        'Huehuetenango'
    ),
    (
        '1324',
        'San Antonio Huista, Huehuetenango',
        'San Antonio Huista',
        'Huehuetenango'
    ),
    (
        '1325',
        'San Sebastián Coatán, Huehuetenango',
        'San Sebastián Coatán',
        'Huehuetenango'
    ),
    (
        '1326',
        'Santa Cruz Barillas, Huehuetenango',
        'Santa Cruz Barillas',
        'Huehuetenango'
    ),
    (
        '1327',
        'Aguacatán, Huehuetenango',
        'Aguacatán',
        'Huehuetenango'
    ),
    (
        '1328',
        'San Rafael Petzal, Huehuetenango',
        'San Rafael Petzal',
        'Huehuetenango'
    ),
    (
        '1329',
        'San Gaspar Ixchil, Huehuetenango',
        'San Gaspar Ixchil',
        'Huehuetenango'
    ),
    (
        '1330',
        'Santiago Chimaltenango, Huehuetenango',
        'Santiago Chimaltenango',
        'Huehuetenango'
    ),
    (
        '1331',
        'Santa Ana Huista, Huehuetenango',
        'Santa Ana Huista',
        'Huehuetenango'
    ),
    (
        '1332',
        'Unión Cantinil, Huehuetenango',
        'Unión Cantinil',
        'Huehuetenango'
    ),
    (
        '1333',
        'Petatán, Huehuetenango',
        'Petatán',
        'Huehuetenango'
    ),
    (
        '1401',
        'Santa Cruz del Quiché, Guatemala',
        'Santa Cruz del Quiché',
        'Guatemala'
    ),
    (
        '1402',
        'Chiché, Guatemala',
        'Chiché',
        'Guatemala'
    ),
    (
        '1403',
        'Chinique, Guatemala',
        'Chinique',
        'Guatemala'
    ),
    (
        '1404',
        'Zacualpa, Guatemala',
        'Zacualpa',
        'Guatemala'
    ),
    (
        '1405',
        'Chajul, Guatemala',
        'Chajul',
        'Guatemala'
    ),
    (
        '1406',
        'Santo Tomás Chichicastenango, Guatemala',
        'Santo Tomás Chichicastenango',
        'Guatemala'
    ),
    (
        '1407',
        'Patzité, Guatemala',
        'Patzité',
        'Guatemala'
    ),
    (
        '1408',
        'San Antonio Ilotenango, Guatemala',
        'San Antonio Ilotenango',
        'Guatemala'
    ),
    (
        '1409',
        'San Pedro Jocopilas, Guatemala',
        'San Pedro Jocopilas',
        'Guatemala'
    ),
    (
        '1410',
        'Cunén, Guatemala',
        'Cunén',
        'Guatemala'
    ),
    (
        '1411',
        'San Juan Cotzal, Guatemala',
        'San Juan Cotzal',
        'Guatemala'
    ),
    (
        '1412',
        'Joyabaj, Guatemala',
        'Joyabaj',
        'Guatemala'
    ),
    (
        '1413',
        'Santa María Nebaj, Guatemala',
        'Santa María Nebaj',
        'Guatemala'
    ),
    (
        '1414',
        'San Andrés Sajcabajá, Guatemala',
        'San Andrés Sajcabajá',
        'Guatemala'
    ),
    (
        '1415',
        'San Miguel Uspantán, Guatemala',
        'San Miguel Uspantán',
        'Guatemala'
    ),
    (
        '1416',
        'Sacapulas, Guatemala',
        'Sacapulas',
        'Guatemala'
    ),
    (
        '1417',
        'San Bartolomé Jocotenango, Guatemala',
        'San Bartolomé Jocotenango',
        'Guatemala'
    ),
    (
        '1418',
        'Canillá, Guatemala',
        'Canillá',
        'Guatemala'
    ),
    (
        '1419',
        'Chicamán, Guatemala',
        'Chicamán',
        'Guatemala'
    ),
    (
        '1420',
        'Playa Grande Ixcán, Guatemala',
        'Playa Grande Ixcán',
        'Guatemala'
    ),
    (
        '1421',
        'Pachalum, Guatemala',
        'Pachalum',
        'Guatemala'
    ),
    (
        '1501',
        'Salamá, Baja Verapaz',
        'Salamá',
        'BajaVerapaz'
    ),
    (
        '1502',
        'San Miguel Chicaj, Baja Verapaz',
        'San Miguel Chicaj',
        'BajaVerapaz'
    ),
    (
        '1503',
        'Rabinal, Baja Verapaz',
        'Rabinal',
        'BajaVerapaz'
    ),
    (
        '1504',
        'Cubulco, Baja Verapaz',
        'Cubulco',
        'BajaVerapaz'
    ),
    (
        '1505',
        'Granados, Baja Verapaz',
        'Granados',
        'BajaVerapaz'
    ),
    (
        '1506',
        'Santa Cruz El Chol, Baja Verapaz',
        'Santa Cruz El Chol',
        'BajaVerapaz'
    ),
    (
        '1507',
        'San Jerónimo, Baja Verapaz',
        'San Jerónimo',
        'BajaVerapaz'
    ),
    (
        '1508',
        'Purulhá, Baja Verapaz',
        'Purulhá',
        'BajaVerapaz'
    ),
    (
        '1601',
        'Cobán, Alta Verapaz',
        'Cobán',
        'AltaVerapaz'
    ),
    (
        '1602',
        'Santa Cruz Verapaz, Alta Verapaz',
        'Santa Cruz Verapaz',
        'AltaVerapaz'
    ),
    (
        '1603',
        'San Cristóbal Verapaz, Alta Verapaz',
        'San Cristóbal Verapaz',
        'AltaVerapaz'
    ),
    (
        '1604',
        'Tactic, Alta Verapaz',
        'Tactic',
        'AltaVerapaz'
    ),
    (
        '1605',
        'Tamahú, Alta Verapaz',
        'Tamahú',
        'AltaVerapaz'
    ),
    (
        '1606',
        'San Miguel Tucurú, Alta Verapaz',
        'San Miguel Tucurú',
        'AltaVerapaz'
    ),
    (
        '1607',
        'Panzós, Alta Verapaz',
        'Panzós',
        'AltaVerapaz'
    ),
    (
        '1608',
        'Senahú, Alta Verapaz',
        'Senahú',
        'AltaVerapaz'
    ),
    (
        '1609',
        'San Pedro Carchá, Alta Verapaz',
        'San Pedro Carchá',
        'AltaVerapaz'
    ),
    (
        '1610',
        'San Juan Chamelco, Alta Verapaz',
        'San Juan Chamelco',
        'AltaVerapaz'
    ),
    (
        '1611',
        'San Agustín Lanquín, Alta Verapaz',
        'San Agustín Lanquín',
        'AltaVerapaz'
    ),
    (
        '1612',
        'Santa María Cahabón, Alta Verapaz',
        'Santa María Cahabón',
        'AltaVerapaz'
    ),
    (
        '1613',
        'Chisec, Alta Verapaz',
        'Chisec',
        'AltaVerapaz'
    ),
    (
        '1614',
        'Chahal, Alta Verapaz',
        'Chahal',
        'AltaVerapaz'
    ),
    (
        '1615',
        'Fray Bartolomé de Las Casas, Alta Verapaz',
        'Fray Bartolomé de Las Casas',
        'AltaVerapaz'
    ),
    (
        '1616',
        'Santa Catalina La Tinta, Alta Verapaz',
        'Santa Catalina La Tinta',
        'AltaVerapaz'
    ),
    (
        '1617',
        'Raxruhá, Alta Verapaz',
        'Raxruhá',
        'AltaVerapaz'
    ),
    (
        '1701',
        'Flores, Petén',
        'Flores',
        'Petén'
    ),
    (
        '1702',
        'San José, Petén',
        'San José',
        'Petén'
    ),
    (
        '1703',
        'San Benito, Petén',
        'San Benito',
        'Petén'
    ),
    (
        '1704',
        'San Andrés, Petén',
        'San Andrés',
        'Petén'
    ),
    (
        '1705',
        'La Libertad, Petén',
        'La Libertad',
        'Petén'
    ),
    (
        '1706',
        'San Francisco, Petén',
        'San Francisco',
        'Petén'
    ),
    (
        '1707',
        'Santa Ana, Petén',
        'Santa Ana',
        'Petén'
    ),
    (
        '1708',
        'Dolores, Petén',
        'Dolores',
        'Petén'
    ),
    (
        '1709',
        'San Luis, Petén',
        'San Luis',
        'Petén'
    ),
    (
        '1710',
        'Sayaxché, Petén',
        'Sayaxché',
        'Petén'
    ),
    (
        '1711',
        'Melchor de Mencos, Petén',
        'Melchor de Mencos',
        'Petén'
    ),
    (
        '1712',
        'Poptún, Petén',
        'Poptún',
        'Petén'
    ),
    (
        '1713',
        'Las Cruces, Petén',
        'Las Cruces',
        'Petén'
    ),
    (
        '1714',
        'El Chal, Petén',
        'El Chal',
        'Petén'
    ),
    (
        '1801',
        'Puerto Barrios, Izabal',
        'Puerto Barrios',
        'Izabal'
    ),
    (
        '1802',
        'Livingston, Izabal',
        'Livingston',
        'Izabal'
    ),
    (
        '1803',
        'El Estor, Izabal',
        'El Estor',
        'Izabal'
    ),
    (
        '1804',
        'Morales, Izabal',
        'Morales',
        'Izabal'
    ),
    (
        '1805',
        'Los Amates, Izabal',
        'Los Amates',
        'Izabal'
    ),
    (
        '1901',
        'Zacapa, Zacapa',
        'Zacapa',
        'Zacapa'
    ),
    (
        '1902',
        'Estanzuela, Zacapa',
        'Estanzuela',
        'Zacapa'
    ),
    (
        '1903',
        'Río Hondo, Zacapa',
        'Río Hondo',
        'Zacapa'
    ),
    (
        '1904',
        'Gualán, Zacapa',
        'Gualán',
        'Zacapa'
    ),
    (
        '1905',
        'Teculután, Zacapa',
        'Teculután',
        'Zacapa'
    ),
    (
        '1906',
        'Usumatlán, Zacapa',
        'Usumatlán',
        'Zacapa'
    ),
    (
        '1907',
        'Cabañas, Zacapa',
        'Cabañas',
        'Zacapa'
    ),
    (
        '1908',
        'San Diego, Zacapa',
        'San Diego',
        'Zacapa'
    ),
    (
        '1909',
        'La Unión, Zacapa',
        'La Unión',
        'Zacapa'
    ),
    (
        '1910',
        'Huité, Zacapa',
        'Huité',
        'Zacapa'
    ),
    (
        '1911',
        'San Jorge, Zacapa',
        'San Jorge',
        'Zacapa'
    ),
    (
        '2001',
        'Chiquimula, Chiquimula',
        'Chiquimula',
        'Chiquimula'
    ),
    (
        '2002',
        'San José La Arada, Chiquimula',
        'San José La Arada',
        'Chiquimula'
    ),
    (
        '2003',
        'San Juan Ermita, Chiquimula',
        'San Juan Ermita',
        'Chiquimula'
    ),
    (
        '2004',
        'Jocotán, Chiquimula',
        'Jocotán',
        'Chiquimula'
    ),
    (
        '2005',
        'Camotán, Chiquimula',
        'Camotán',
        'Chiquimula'
    ),
    (
        '2006',
        'Olopa, Chiquimula',
        'Olopa',
        'Chiquimula'
    ),
    (
        '2007',
        'Esquipulas, Chiquimula',
        'Esquipulas',
        'Chiquimula'
    ),
    (
        '2008',
        'Concepción Las Minas, Chiquimula',
        'Concepción Las Minas',
        'Chiquimula'
    ),
    (
        '2009',
        'Quezaltepeque, Chiquimula',
        'Quezaltepeque',
        'Chiquimula'
    ),
    (
        '2010',
        'San Jacinto, Chiquimula',
        'San Jacinto',
        'Chiquimula'
    ),
    (
        '2011',
        'Ipala, Chiquimula',
        'Ipala',
        'Chiquimula'
    ),
    (
        '2101',
        'Jalapa, Jalapa',
        'Jalapa',
        'Jalapa'
    ),
    (
        '2102',
        'San Pedro Pinula, Jalapa',
        'San Pedro Pinula',
        'Jalapa'
    ),
    (
        '2103',
        'San Luis Jilotepeque, Jalapa',
        'San Luis Jilotepeque',
        'Jalapa'
    ),
    (
        '2104',
        'San Manuel Chaparrón, Jalapa',
        'San Manuel Chaparrón',
        'Jalapa'
    ),
    (
        '2105',
        'San Carlos Alzatate, Jalapa',
        'San Carlos Alzatate',
        'Jalapa'
    ),
    (
        '2106',
        'Monjas, Jalapa',
        'Monjas',
        'Jalapa'
    ),
    (
        '2107',
        'Mataquescuintla, Jalapa',
        'Mataquescuintla',
        'Jalapa'
    ),
    (
        '2201',
        'Jutiapa, Jutiapa',
        'Jutiapa',
        'Jutiapa'
    ),
    (
        '2202',
        'El Progreso, Jutiapa',
        'El Progreso',
        'Jutiapa'
    ),
    (
        '2203',
        'Santa Catarina Mita, Jutiapa',
        'Santa Catarina Mita',
        'Jutiapa'
    ),
    (
        '2204',
        'Agua Blanca, Jutiapa',
        'Agua Blanca',
        'Jutiapa'
    ),
    (
        '2205',
        'Asunción Mita, Jutiapa',
        'Asunción Mita',
        'Jutiapa'
    ),
    (
        '2206',
        'Yupiltepeque, Jutiapa',
        'Yupiltepeque',
        'Jutiapa'
    ),
    (
        '2207',
        'Atescatempa, Jutiapa',
        'Atescatempa',
        'Jutiapa'
    ),
    (
        '2208',
        'Jerez, Jutiapa',
        'Jerez',
        'Jutiapa'
    ),
    (
        '2209',
        'El Adelanto, Jutiapa',
        'El Adelanto',
        'Jutiapa'
    ),
    (
        '2210',
        'Zapotitlán, Jutiapa',
        'Zapotitlán',
        'Jutiapa'
    ),
    (
        '2211',
        'Comapa, Jutiapa',
        'Comapa',
        'Jutiapa'
    ),
    (
        '2212',
        'Jalpatagua, Jutiapa',
        'Jalpatagua',
        'Jutiapa'
    ),
    (
        '2213',
        'Conguaco, Jutiapa',
        'Conguaco',
        'Jutiapa'
    ),
    (
        '2214',
        'Moyuta, Jutiapa',
        'Moyuta',
        'Jutiapa'
    ),
    (
        '2215',
        'Pasaco, Jutiapa',
        'Pasaco',
        'Jutiapa'
    ),
    (
        '2216',
        'San José Acatempa, Jutiapa',
        'San José Acatempa',
        'Jutiapa'
    ),
    (
        '2217',
        'Quesada, Jutiapa',
        'Quesada',
        'Jutiapa'
    );