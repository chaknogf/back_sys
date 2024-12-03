-- Iniciar la transacción para garantizar que todo se actualice de manera segura
START TRANSACTION;

-- Lote 1: Actualizar los primeros 1000 registros
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 1 AND 1000;

-- Lote 2: Actualizar los siguientes 1000 registros (del 1001 al 2000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 1001 AND 2000;

-- Lote 3: Actualizar los siguientes 1000 registros (del 2001 al 3000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 2001 AND 3000;

-- Lote 4: Actualizar los siguientes 1000 registros (del 3001 al 4000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 3001 AND 4000;

-- Lote 5: Actualizar los siguientes 1000 registros (del 4001 al 5000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 4001 AND 5000;

-- Lote 6: Actualizar los siguientes 1000 registros (del 5001 al 6000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 5001 AND 6000;

-- Lote 7: Actualizar los siguientes 1000 registros (del 6001 al 7000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 6001 AND 7000;

-- Lote 8: Actualizar los siguientes 1000 registros (del 7001 al 8000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 7001 AND 8000;

-- Lote 9: Actualizar los siguientes 1000 registros (del 8001 al 9000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 8001 AND 9000;

-- Lote 10: Actualizar los siguientes 1000 registros (del 9001 al 10000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 9001 AND 10000;

-- Lote 11: Actualizar los siguientes 1000 registros (del 10001 al 11000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 10001 AND 11000;

-- Lote 12: Actualizar los siguientes 1000 registros (del 11001 al 12000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 11001 AND 12000;

-- Lote 13: Actualizar los siguientes 1000 registros (del 12001 al 13000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 12001 AND 13000;

-- Lote 14: Actualizar los siguientes 1000 registros (del 13001 al 14000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 13001 AND 14000;

-- Lote 15: Actualizar los siguientes 1000 registros (del 14001 al 15000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 14001 AND 15000;

-- Lote 16: Actualizar los siguientes 1000 registros (del 15001 al 16000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 15001 AND 16000;

-- Lote 17: Actualizar los siguientes 1000 registros (del 16001 al 17000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 16001 AND 17000;

-- Lote 18: Actualizar los siguientes 1000 registros (del 17001 al 18000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 17001 AND 18000;

-- Lote 19: Actualizar los siguientes 1000 registros (del 18001 al 19000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 18001 AND 19000;

-- Lote 20: Actualizar los siguientes 1000 registros (del 19001 al 20000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 19001 AND 20000;

-- Lote 21: Actualizar los siguientes 1000 registros (del 20001 al 21000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 20001 AND 21000;

-- Lote 22: Actualizar los siguientes 1000 registros (del 21001 al 22000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 21001 AND 22000;

-- Lote 23: Actualizar los siguientes 1000 registros (del 22001 al 23000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 22001 AND 23000;

-- Lote 24: Actualizar los siguientes 1000 registros (del 23001 al 24000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 23001 AND 24000;

-- Lote 25: Actualizar los siguientes 1000 registros (del 24001 al 25000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 24001 AND 25000;

-- Lote 26: Actualizar los siguientes 1000 registros (del 25001 al 26000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 25001 AND 26000;

-- Lote 27: Actualizar los siguientes 1000 registros (del 26001 al 27000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 26001 AND 27000;

-- Lote 28: Actualizar los siguientes 1000 registros (del 27001 al 28000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 27001 AND 28000;

-- Lote 29: Actualizar los siguientes 1000 registros (del 28001 al 29000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 28001 AND 29000;

UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 29001 AND 30000;

-- Lote 2: Actualizar los siguientes 1000 registros (del 1001 al 2000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 30001 AND 31000;

-- Lote 3: Actualizar los siguientes 1000 registros (del 2001 al 3000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 31001 AND 32000;

-- Lote 4: Actualizar los siguientes 1000 registros (del 3001 al 4000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 32001 AND 33000;

-- Lote 5: Actualizar los siguientes 1000 registros (del 4001 al 5000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 33001 AND 34000;

-- Lote 6: Actualizar los siguientes 1000 registros (del 5001 al 6000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 34001 AND 35000;

-- Lote 7: Actualizar los siguientes 1000 registros (del 6001 al 7000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 35001 AND 36000;

-- Lote 8: Actualizar los siguientes 1000 registros (del 7001 al 8000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 36001 AND 37000;

-- Lote 9: Actualizar los siguientes 1000 registros (del 8001 al 9000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 38001 AND 39000;

-- Lote 10: Actualizar los siguientes 1000 registros (del 9001 al 10000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 39001 AND 40000;

-- Lote 11: Actualizar los siguientes 1000 registros (del 10001 al 11000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 40001 AND 41000;

-- Lote 12: Actualizar los siguientes 1000 registros (del 11001 al 12000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 41001 AND 42000;

-- Lote 13: Actualizar los siguientes 1000 registros (del 12001 al 13000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 42001 AND 43000;

-- Lote 14: Actualizar los siguientes 1000 registros (del 13001 al 14000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 43001 AND 44000;

-- Lote 15: Actualizar los siguientes 1000 registros (del 14001 al 15000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 44001 AND 45000;

-- Lote 16: Actualizar los siguientes 1000 registros (del 15001 al 16000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 45001 AND 46000;

-- Lote 17: Actualizar los siguientes 1000 registros (del 16001 al 17000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 46001 AND 47000;

-- Lote 18: Actualizar los siguientes 1000 registros (del 17001 al 18000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 47001 AND 48000;

-- Lote 19: Actualizar los siguientes 1000 registros (del 18001 al 19000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 48001 AND 49000;

-- Lote 20: Actualizar los siguientes 1000 registros (del 19001 al 20000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 49001 AND 50000;

-- Lote 21: Actualizar los siguientes 1000 registros (del 20001 al 21000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 50001 AND 51000;

-- Lote 22: Actualizar los siguientes 1000 registros (del 21001 al 22000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 51001 AND 52000;

-- Lote 23: Actualizar los siguientes 1000 registros (del 22001 al 23000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 52001 AND 53000;

-- Lote 24: Actualizar los siguientes 1000 registros (del 23001 al 24000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 53001 AND 54000;

-- Lote 25: Actualizar los siguientes 1000 registros (del 24001 al 25000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 54001 AND 55000;

-- Lote 26: Actualizar los siguientes 1000 registros (del 25001 al 26000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 55001 AND 56000;

-- Lote 27: Actualizar los siguientes 1000 registros (del 26001 al 27000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 56001 AND 57000;

-- Lote 28: Actualizar los siguientes 1000 registros (del 27001 al 28000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 57001 AND 58000;

-- Lote 29: Actualizar los siguientes 1000 registros (del 28001 al 29000)
UPDATE nuevaconsulta nc
JOIN nuevaexpediente ne ON nc.expediente = ne.expediente
SET
    nc.consulta_id = ne.id
WHERE
    nc.id BETWEEN 58001 AND 59000;