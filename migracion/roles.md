# Gestión de Roles y Permisos en SQL

## 1. Crear Tablas

```sql
-- Tabla de Roles
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de Permisos
CREATE TABLE permisos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla Intermedia: Roles-Permisos
CREATE TABLE roles_permisos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rol_id INT NOT NULL,
    permiso_id INT NOT NULL,
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
);

-- Tabla de Usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE SET NULL
);

-- Tabla Intermedia: Usuarios-Permisos (Opcional, para permisos individuales)
CREATE TABLE usuarios_permisos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    permiso_id INT NOT NULL,
    tiene_permiso BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
);

INSERT INTO roles (nombre, descripcion)
VALUES
    ('Admin', 'Acceso total al sistema'),
    ('Editor', 'Puede editar y crear contenido'),
    ('Viewer', 'Solo puede visualizar contenido');


INSERT INTO permisos (nombre, descripcion)
VALUES
    ('Crear usuario', 'Permiso para crear usuarios nuevos'),
    ('Editar post', 'Permiso para editar publicaciones'),
    ('Ver post', 'Permiso para visualizar publicaciones');

INSERT INTO roles_permisos (rol_id, permiso_id)
VALUES
    (1, 1), -- Admin puede 'Crear usuario'
    (1, 2), -- Admin puede 'Editar post'
    (1, 3), -- Admin puede 'Ver post'
    (2, 2), -- Editor puede 'Editar post'
    (2, 3), -- Editor puede 'Ver post'
    (3, 3); -- Viewer puede 'Ver post'

INSERT INTO usuarios (username, name, email, password, rol_id)
VALUES
    ('admin_user', 'Admin User', 'admin@example.com', 'hashed_password', 1), -- Admin
    ('editor_user', 'Editor User', 'editor@example.com', 'hashed_password', 2), -- Editor
    ('viewer_user', 'Viewer User', 'viewer@example.com', 'hashed_password', 3); -- Viewer

INSERT INTO usuarios_permisos (usuario_id, permiso_id, tiene_permiso)
VALUES
    (2, 1, TRUE), -- Usuario con id 2 (Editor) obtiene permiso 'Crear usuario'
    (3, 2, FALSE); -- Usuario con id 3 (Viewer) se le niega el permiso 'Editar post'

SELECT p.nombre AS permiso
FROM usuarios u
JOIN roles r ON u.rol_id = r.id
JOIN roles_permisos rp ON r.id = rp.rol_id
JOIN permisos p ON rp.permiso_id = p.id
WHERE u.id = 1; -- Reemplazar con el ID del usuario


SELECT p.nombre AS permiso, up.tiene_permiso
FROM usuarios_permisos up
JOIN permisos p ON up.permiso_id = p.id
WHERE up.usuario_id = 2; -- Reemplazar con el ID del usuario

UPDATE roles_permisos
SET permiso_id = 2
WHERE rol_id = 1 AND permiso_id = 1; -- Actualiza el permiso asociado al rol Admin

DELETE FROM roles WHERE id = 3; -- Elimina el rol Viewer

DELETE FROM permisos WHERE id = 1; -- Elimina el permiso 'Crear usuario'

DELETE FROM usuarios WHERE id = 2; -- Elimina el usuario Editor
```
