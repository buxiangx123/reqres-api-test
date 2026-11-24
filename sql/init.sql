-- CI 用的库/表初始化，结构对齐本地，但建表即 utf8mb4（规避 latin1 中文 500）
CREATE TABLE IF NOT EXISTS users (
    id         INT(11)      NOT NULL AUTO_INCREMENT,
    username   VARCHAR(50)  NOT NULL,
    email      VARCHAR(100) NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;